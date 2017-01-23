from __future__ import absolute_import

import logging

from numpy import ascontiguousarray
from numpy import logical_not
from numpy import isfinite
from numpy import newaxis
from numpy import argsort

from ..util import gower_normalization
from ..util import clone

from ._core import train_associations


def normal_scan(y, covariates, X, K):
    logger = logging.getLogger(__name__)
    logger.info('Gower normalizing')

    y = clone(y)
    X = clone(X)
    K = clone(K)
    covariates = clone(covariates)

    gower_normalization(K, out=K)

    y -= y.mean()
    std = y.std()
    if std > 0.:
        y /= std

    y = y[:, newaxis]

    logger.info('train_association started')
    (stats, pvals, _, _, _) = train_associations(X, y, K, C=covariates,
                                             addBiasTerm=False)
    logger.info('train_association finished')
    pvals = ascontiguousarray(pvals, float).ravel()
    nok = logical_not(isfinite(pvals))
    pvals[nok] = 1.

    return pvals

def bernoulli_scan(outcome, X, K, covariates):
    logger = logging.getLogger(__name__)
    logger.info('Gower normalizing')

    outcome = clone(outcome)
    X = clone(X)
    K = clone(K)
    covariates = clone(covariates)

    gower_normalization(K, out=K)

    outcome -= outcome.mean()
    std = outcome.std()
    if std > 0.:
        outcome /= std

    outcome = outcome[:, newaxis]

    logger.info('train_association started')
    (stats, pvals, _, _, _) = train_associations(X, outcome, K, C=covariates,
                                                 addBiasTerm=False)
    logger.info('train_association finished')
    pvals = ascontiguousarray(pvals, float).ravel()
    nok = logical_not(isfinite(pvals))
    pvals[nok] = 1.

    stats = ascontiguousarray(stats, float).ravel()
    stats[nok] = 0.

    return pvals


def binomial_scan(nsuccesses, ntrials, X, K, covariates, rank_normalize=False):
    logger = logging.getLogger(__name__)

    from lim.util.preprocessing import quantile_gaussianize
    logger.info('Gower normalizing')

    nsuccesses = clone(nsuccesses)
    ntrials = clone(ntrials)
    X = clone(X)
    K = clone(K)
    covariates = clone(covariates)

    gower_normalization(K, out=K)

    nsuccesses /= ntrials

    nsuccesses -= nsuccesses.mean()
    std = nsuccesses.std()
    if std > 0.:
        nsuccesses /= std

    if rank_normalize:
        nsuccesses = quantile_gaussianize(nsuccesses)

    nsuccesses = nsuccesses[:, newaxis]

    logger.info('train_association started')
    (stats, pvals, _, _, _) = train_associations(X, nsuccesses, K, C=covariates,
                                                 addBiasTerm=False)
    logger.info('train_association finished')
    pvals = ascontiguousarray(pvals, float).ravel()
    nok = logical_not(isfinite(pvals))
    pvals[nok] = 1.

    stats = ascontiguousarray(stats, float).ravel()
    stats[nok] = 0.

    return pvals

def poisson_scan(noccurrences, X, K, covariates):
    logger = logging.getLogger(__name__)
    logger.info('Gower normalizing')

    noccurrences = clone(noccurrences)
    X = clone(X)
    K = clone(K)
    covariates = clone(covariates)

    gower_normalization(K, out=K)

    noccurrences -= noccurrences.mean()
    std = noccurrences.std()
    if std > 0.:
        noccurrences /= std

    noccurrences = noccurrences[:, newaxis]

    logger.info('train_association started')
    (stats, pvals, _, _, _) = train_associations(X, noccurrences, K,
                                                 C=covariates,
                                                 addBiasTerm=False)
    logger.info('train_association finished')
    pvals = ascontiguousarray(pvals, float).ravel()
    nok = logical_not(isfinite(pvals))
    pvals[nok] = 1.

    stats = ascontiguousarray(stats, float).ravel()
    stats[nok] = 0.

    return pvals
