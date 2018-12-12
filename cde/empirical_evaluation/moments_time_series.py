from cde.density_estimator.MDN import MixtureDensityNetwork
from cde.empirical_evaluation.load_dataset import make_overall_eurostoxx_df, target_feature_split

import numpy as np
import time
import os
import pandas as pd
from matplotlib import pyplot as plt

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))

def main():

  t = time.time()
  # 1) load data
  df = make_overall_eurostoxx_df()

  X, Y, features = target_feature_split(df, 'log_ret_1', filter_nan=True, return_features=True)
  X, Y = np.array(X), np.array(Y)
  ndim_x, ndim_y = X.shape[1], 1

  # 2) Fite density model
  mdn = MixtureDensityNetwork('mdn_empirical_no_pca', ndim_x, ndim_y, n_centers=20, n_training_epochs=10,
                              random_seed=22, x_noise_std=0.2, y_noise_std=0.1)
  mdn.fit(X,Y)

  # 3) estimate moments
  n_samples = 10**7
  print('compute mean')
  mean = np.squeeze(mdn.mean_(x_cond=X, n_samples=n_samples))
  print('compute cov')
  cov = np.squeeze(mdn.covariance(x_cond=X, n_samples=n_samples))
  print('compute skewness')
  skew = mdn._skewness_mc(x_cond=X, n_samples=n_samples)
  print('compute kurtosis')
  kurt = mdn._kurtosis_mc(x_cond=X, n_samples=n_samples)

  # 4) save data
  data = np.stack([mean, cov, skew, kurt], axis=-1)
  moments_df = pd.DataFrame(data=data, index=df.dropna().index, columns=['mean', 'variance', 'skewness', 'kurtosis'])
  print(moments_df)

  # dump csv
  dump_dir = os.path.join(DATA_DIR, 'moments_time_series')
  if not os.path.exists(dump_dir):
    os.makedirs(dump_dir)
  moments_df.to_csv(os.path.join(dump_dir, 'moments_time_series.csv'))

  fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(15, 20))

  x = moments_df.index
  for i in range(4):
    label = moments_df.columns[i]
    y = moments_df.ix[:, i]
    axes[i].plot(x, y)
    axes[i].set_title(label)
  plt.show()
  plt.savefig(os.path.join(dump_dir, 'moments_time_series.png'))
  print("Compute time:", time.time() - t)

if __name__ == '__main__':
  main()
