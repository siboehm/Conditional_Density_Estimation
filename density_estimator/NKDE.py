import numpy as np
from sklearn.base import BaseEstimator
from density_estimator.helpers import norm_along_axis_1, handle_input_dimensionality
from sklearn.preprocessing import normalize
from scipy.stats import multivariate_normal
import warnings

class NeighborKernelDensityEstimation(BaseEstimator):
  """
  Epsilon-Neighbor Kernel Density Estimation (lazy learner)
  """

  def __init__(self, epsilon=5.0, bandwidth=1.0, weighted=True):
    """
    Constructor for Epsilon-Neighbor Kernel Density Estimation
    :param epsilon: size of the neighborhood region
    :param bandwidth: variance of the Gaussians
    :param weighted: true - the neighborhood Gaussians are weighted according to their distance to the query point, false - all neighborhood Gaussians are weighted equally
    """
    self.epsilon = epsilon
    self.weighted = weighted
    self.bandwidth = bandwidth

    self.fitted = False

  def fit(self, X, Y):
    """
    lazy learner - stores the learning data X and Y
    :param X: nummpy array to be conditioned on - shape: (n_samples, n_dim_x)
    :param Y: nummpy array of y targets - shape: (n_samples, n_dim_y)
    """
    # assert that both X an Y are 2D arrays with shape (n_samples, n_dim)
    x, Y = handle_input_dimensionality(X, Y)

    self.ndim_y, self.ndim_x = Y.shape[1], X.shape[1]

    self._build_model(X, Y)

    self.fitted = True


  def _build_model(self, X, Y):
    self.n_train_points = X.shape[0]

    # lazy learner - just store training data
    self.X_train = X
    self.Y_train = Y

    # prepare Gaussians centered in the Y points
    self.locs_array = np.vsplit(Y, self.n_train_points)
    self.scales = np.diag(self.bandwidth * np.ones(self.ndim_y))
    self.components = [multivariate_normal(mean=loc, cov=self.scales) for loc in self.locs_array]


  def predict(self, X, Y):
    """
    copmutes the contitional likelihood p(y|x) given the fitted model
    :param X: nummpy array to be conditioned on - shape: (n_query_samples, n_dim_x)
    :param Y: nummpy array of y targets - shape: (n_query_samples, n_dim_y)
    :return: numpy array of shape (n_query_samples, ) holding the conditional likelihood p(y|x)
    """

    # assert that both X an Y are 2D arrays with shape (n_samples, n_dim)
    X, Y = handle_input_dimensionality(X, Y)
    assert X.shape[1] == self.ndim_x
    assert Y.shape[1] == self.ndim_y

    """ 1. Determine weights of the Gaussians """
    X_dist = norm_along_axis_1(X, self.X_train)

    # filter out all points that are not in a epsilon region of x
    mask = X_dist > self.epsilon
    neighbor_distances = np.ma.masked_where(mask, X_dist)
    num_neighbors = neighbor_distances.count(axis=1)

    if self.weighted:
      # neighbors are weighted in proportion to their distance to the query point
      neighbor_weights = normalize(neighbor_distances.filled(fill_value=0), norm='l1', axis=1)
    else:
      # all neighbors are weighted equally
      with warnings.catch_warnings():
        warnings.simplefilter("ignore") # don't print division by zero warning
        weights = 1 / num_neighbors
      neighbor_weights = neighbor_distances.copy()
      neighbor_weights[:] = weights[:, None]
      neighbor_weights = np.ma.masked_where(mask, neighbor_weights)

      neighbor_weights = neighbor_weights.filled(fill_value=0)

    """ 2. Calculate the conditional densities """
    n_samples = X.shape[0]

    conditional_densities = np.zeros(n_samples)
    for i in range(n_samples):
      conditional_densities[i] = self._density(neighbor_weights[i, :], Y[i, :])

    return conditional_densities


  def _density(self, neighbor_weights, y):
    assert neighbor_weights.shape[0] == self.n_train_points
    assert y.shape[0] == self.ndim_y
    kernel_ids = np.arange(self.n_train_points)

    # vectorized function
    single_densities = np.vectorize(self._single_density, otypes=[np.float])

    # call vectorized function
    single_den = single_densities(neighbor_weights, kernel_ids, y)

    return np.sum(single_den)


  def _single_density(self, neighbor_weight, kernel_id, y):
    if neighbor_weight > 0:
      return neighbor_weight * self.components[kernel_id].pdf(y)
    else:
      return 0






