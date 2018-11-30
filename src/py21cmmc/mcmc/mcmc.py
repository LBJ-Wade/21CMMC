from os import path, mkdir

from .cosmoHammer import CosmoHammerSampler, LikelihoodComputationChain, HDFStorageUtil, Params


def build_computation_chain(core_modules, likelihood_modules, params=None):
    """
    Build a likelihood computation chain from core and likelihood modules.

    Parameters
    ----------
    core_modules : list
        A list of objects which define the necessary methods to be core modules (see :mod:`~py21cmmc.mcmc.core`).
    likelihood_modules : list
        A list of objects which define the necessary methods to be likelihood modules (see
        :mod:`~py21cmmc.mcmc.likelihood`)
    params : :class:`~py21cmmc.mcmc.cosmoHammer.util.Params`, optional
        If provided, parameters which will be sampled by the chain.

    Returns
    -------
    chain : :class:`py21cmmc.mcmc.cosmoHammer.LikelihoodComputationChain.LikelihoodComputationChain`
    """
    if not hasattr(core_modules, "__len__"):
        core_modules = [core_modules]

    if not hasattr(likelihood_modules, "__len__"):
        likelihood_modules = [likelihood_modules]

    chain = LikelihoodComputationChain(params)

    for cm in core_modules:
        chain.addCoreModule(cm)

    for lk in likelihood_modules:
        chain.addLikelihoodModule(lk)

    chain.setup()
    return chain


def run_mcmc(core_modules, likelihood_modules, params,
             datadir='.', model_name='21CMMC',
             continue_sampling=True, reuse_burnin=True,
             **mcmc_options):
    """

    Parameters
    ----------
    core_modules : list
        A list of objects which define the necessary methods to be core modules (see :mod:`~py21cmmc.mcmc.core`).
    likelihood_modules : list
        A list of objects which define the necessary methods to be likelihood modules (see
        :mod:`~py21cmmc.mcmc.likelihood`)
    params : dict
        Parameters which will be sampled by the chain. Each entry's key specifies the name of the parameter, and
        its value is an iterable `(val, min, max, width)`, with `val` the initial guess, `min` and `max` the hard
        boundaries on the parameter's value, and `width` determining the size of the initial ball of walker positions
        for the parameter.
    datadir : str, optional
        Directory to which MCMC info will be written (eg. logs and chain files)
    model_name : str, optional
        Name of the model, which determines filenames of outputs.
    continue_sampling : bool, optional
        If an output chain file can be found that matches these inputs, sampling can be continued from its last
        iteration, up to the number of iterations specified. If set to `False`, any output file which matches these
        parameters will have its samples over-written.
    reuse_burnin : bool, optional
        If a pre-computed chain file is found, and `continue_sampling=False`, setting `reuse_burnin` will salvage
        the burnin part of the chain for re-use, but re-compute the samples themselves.

    Other Parameters
    ----------------
    All other parameters are passed directly to :class:`~py21cmmc.mcmc.cosmoHammer.CosmoHammerSampler.CosmoHammerSampler`.
    These include important options such as `walkersRatio` (the number of walkers is ``walkersRatio*nparams``),
    `sampleIterations`, `burninIterations` and `threadCount`.

    Returns
    -------
    sampler : `~py21cmmc.mcmc.cosmoHammer.CosmoHammerSampler.CosmoHammerSampler` instance.
        The sampler object, from which the chain itself may be accessed (via the ``samples`` attribute).
    """
    file_prefix = path.join(datadir, model_name)

    try:
        mkdir(datadir)
    except FileExistsError:
        pass

    # Setup parameters.
    if not isinstance(params, Params):
        params = Params(*[(k, v) for k, v in params.items()])

    chain = build_computation_chain(core_modules, likelihood_modules, params)

    sampler = CosmoHammerSampler(
        continue_sampling=continue_sampling,
        likelihoodComputationChain=chain,
        storageUtil=HDFStorageUtil(file_prefix),
        filePrefix=file_prefix,
        reuseBurnin=reuse_burnin,
        **mcmc_options
    )

    # The sampler writes to file, so no need to save anything ourselves.
    sampler.startSampling()

    return sampler
