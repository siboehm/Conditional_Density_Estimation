# Nonparametric_Density_Estimation
todo


## edward issues
- https://github.com/blei-lab/edward/issues/874
- https://stackoverflow.com/questions/49435335/check-if-noise-is-really-used-during-training-with-keras-edward-and-tensorflow

## tensorflow issues
- on workstations with ferreira account execute ```source activate p3.6```
- use tensorflow-gpu==1.2.0

### tf version 1.1
tensorflow version 1.1 works with installed cuDNN but "python3 density_estimator_tests.py" yields
"AttributeError: module 'tensorflow.contrib.distributions' has no attribute 'bijectors'", work-arounds on google don't help

### tf version > 1.2 <= 1.4 
importing tensorflow yields:
ImportError: /common/homes/students/ferreira/anaconda3/envs/p3.6/lib/python3.6/site-packages/tensorflow/python/../libtensorflow_framework.so: undefined symbol: cudnnSetRNNDescriptor_v6
-> cuDNN 6 not properly installed, cuDNN 5 works
### tf version > 1.4
- cuda 9 and cudnn 7 required
- see https://www.tensorflow.org/install/install_sources#tested_source_configurations for cuDNN and cuda requirements


```
cat /usr/local/cuda/include/cudnn.h | grep CUDNN_MAJOR -A 2
cat /usr/include/x86_64-linux-gnu/cudnn_v*.h | grep CUDNN_MAJOR -A 2
```

```
check libcudnn 
libcudnn.so.6 -> libcudnn.so.6.0.21 (changed)
libcudnn.so.5 -> libcudnn.so.6 (changed)
libcudnn.so.5 -> libcudnn.so.6
libcudnn.so.6 -> libcudnn.so.6.0.21
libcudnn is installed
```