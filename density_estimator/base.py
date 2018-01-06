from sklearn.base import BaseEstimator
from sklearn.model_selection import cross_val_score, GridSearchCV
import numpy as np
import warnings

class BaseDensityEstimator(BaseEstimator):

  def fit(self, X, Y):
    raise NotImplementedError

  def predict(self, X, Y):
    raise NotImplementedError

  def predict_density(self, X, Y=None, resolution=50):
    raise NotImplementedError

  def _param_grid(self):
    raise NotImplementedError

  def score(self, X, Y):
    """
    computes the conditional log-likelihood of the provided data (X, Y)
    :param X: nummpy array to be conditioned on - shape: (n_query_samples, n_dim_x)
    :param Y: nummpy array of y targets - shape: (n_query_samples, n_dim_y)
    :return: negative log likelihood of data
    """
    assert self.fitted, "model must be fitted to compute likelihood score"
    with warnings.catch_warnings():
      warnings.simplefilter("ignore")  # don't print division by zero warning
      conditional_log_likelihoods = np.log(self.predict(X, Y))
    return np.sum(conditional_log_likelihoods)

  def fit_by_cv(self, X, Y, n_folds=5):
    # save properties of data
    self.n_samples = X.shape[0]
    self.x_std = np.std(X, axis=0)
    self.y_std = np.std(Y, axis=0)

    param_grid = self._param_grid()
    cv_model = GridSearchCV(self, param_grid, fit_params=None, n_jobs=-1, refit=True, cv=n_folds,
                 verbose=1)
    with warnings.catch_warnings():
      warnings.simplefilter("ignore")  # don't print division by zero warning
      cv_model.fit(X,Y)
    best_params = cv_model.best_params_
    print("Cross-Validation terminated")
    print("Best likelihood score: %.4f"%cv_model.best_score_)
    print("Best params:", best_params)
    self.set_params(**cv_model.best_params_)
    self.fit(X,Y)

  def _handle_input_dimensionality(self, X, Y, fitting=False):
    # assert that both X an Y are 2D arrays with shape (n_samples, n_dim)
    if X.ndim == 1:
      X = np.expand_dims(X, axis=1)
    if Y.ndim == 1:
      Y = np.expand_dims(Y, axis=1)

    assert X.shape[0] == Y.shape[0], "X and Y must have the same length along axis 0"
    assert X.ndim == Y.ndim == 2, "X and Y must be matrices"

    if fitting: # store n_dim of training data
      self.ndim_y, self.ndim_x = Y.shape[1], X.shape[1]
    else:
      assert X.shape[1] == self.ndim_x, "X must have shape (?, %i) but provided X has shape %s" % (self.ndim_x, X.shape)
      assert Y.shape[1] == self.ndim_y, "Y must have shape (?, %i) but provided Y has shape %s" % (self.ndim_y, Y.shape)
    return X, Y