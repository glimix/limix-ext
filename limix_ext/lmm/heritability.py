from __future__ import division
import numpy as np
from numpy import asarray
from limix_tool.heritability import h2_observed_space_correct
from limix_tool.kinship import gower_kinship_normalization
import scipy as sp
import scipy.stats
import core

def estimate(y, covariate, K, prevalence, ntrials=None, **kwargs):
    y = asarray(y, float).copy()
    if ntrials is None:
        return _bernoulli_estimator(y, covariate, K, prevalence, **kwargs)
    return _binomial_estimator(y, covariate, K, ntrials, prevalence, **kwargs)

def _binomial_estimator(y, covariate, K, ntrials, prevalence, **kwargs):

    do_snoise = kwargs.get('estimate_sampling_noise', False)
    ilink = kwargs.get('ilink', True)

    sign2 = 0
    if do_snoise:
        p = y / ntrials
        sign2 = np.mean(ntrials * p * (1 - p))


    y = y.copy() / ntrials
    covariate = covariate.copy()

    if ilink:
        y = np.clip(sp.stats.norm.isf(1-y), -8.2, +8.2)
    else:
        y -= y.mean()
        std = y.std()
        if std > 0.:
            y /= std
    K = gower_kinship_normalization(asarray(K, float))

    n = K.shape[0]
    G = np.random.randint(0, 3, size=(n, 1))
    G = np.asarray(G, float)
    y_ = y[:, np.newaxis]

    (_, _, ldelta, sigg2, beta0) = core.train_associations(G, y_,
                                                  K, C=covariate,
                                                  addBiasTerm=False)

    m = np.dot(covariate, beta0.T)
    varc = np.var(m)

    delta = np.exp(ldelta)
    sige2 = delta * sigg2
    h2 = sigg2 / (sigg2 + sige2 + varc + sign2)
    h2 = np.asscalar(np.asarray(h2, float))

    h2 = h2_observed_space_correct(h2, prevalence, prevalence)

    if not np.isfinite(h2):
        h2 = 0.
    return h2


def _bernoulli_estimator(y, covariate, K, prevalence, **kwargs):
    y = y.copy()
    covariate = covariate.copy()
    ascertainment = float(sum(y==1.)) / len(y)
    y -= y.mean()
    std = y.std()
    if std > 0.:
        y /= std
    K = gower_kinship_normalization(asarray(K, float))

    n = K.shape[0]
    G = np.random.randint(0, 3, size=(n, 1))
    G = np.asarray(G, float)
    y_ = y[:, np.newaxis]

    (_, _, ldelta, sigg2, beta0) = core.train_associations(G, y_,
                                                  K, C=covariate,
                                                  addBiasTerm=False)

    m = np.dot(covariate, beta0.T)
    varc = np.var(m)

    delta = np.exp(ldelta)
    sige2 = delta * sigg2
    h2 = sigg2 / (sigg2 + sige2 + varc)
    h2 = np.asscalar(np.asarray(h2, float))

    h2 = h2_observed_space_correct(h2, prevalence, ascertainment)

    if not np.isfinite(h2):
        h2 = 0.
    return h2
