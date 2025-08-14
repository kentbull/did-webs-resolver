import json
from typing import List

from hio.base import Doer, doing
from keri.app import oobiing
from keri.app.configing import Configer
from keri.app.habbing import Habery
from keri.vdr.credentialing import Regery

from dws import log_name, ogler
from dws.core import artifacting, habs

logger = ogler.getLogger(log_name)


class DIDArtifactGenerator(doing.DoDoer):
    """
    Generates a did:webs DID document and the associated CESR stream for the {AID}.json and keri.cesr files.
    - {AID}.json contains the DID document
    - keri.cesr contains the CESR event stream for the KELs, TELs, and ACDCs associated with the DID.
    """

    def __init__(
        self,
        name: str,
        base: str | None,
        bran: str | None,
        did: str,
        meta: bool = False,
        output_dir: str = '.',
        verbose: bool = False,
        config_dir: str | None = None,
        config_file: str | None = None,
        cf: Configer | None = None,
        hby: Habery | None = None,
        hby_doer: Doer | None = None,
        regery: Regery | None = None,
    ):
        """
        Initializes the did:webs DID file generator.

        Parameters:
            name (str): Name of the controller keystore (Habery) to use for generating the DID document.
            base (str): Base path (namespace for local file tree) for the KERI keystore (Habery) to use for generating the DID document.
            bran (str): Passcode for the controller of the local KERI keystore.
            did (str): The did:webs DID showing the domain and AID to generate the DID document and CESR stream for.
            meta (bool): Whether to include metadata in the DID document generation. Defaults to False.
            output_dir (str): Directory to output the generated files. Default is current directory.
            verbose (bool): Whether to print the generated DID artifacts at the command line. Defaults to False
            config_dir (str): Directory override for configuration data. Defaults to None.
            config_file (str): Configuration filename override. Defaults to None.
            cf (Configer): Optional Configer instance to use for configuration. If None, it will be created based on the provided parameters.
            hby (Habery): Optional Habery instance to use. If None, it will be created based on the provided parameters.
            hby_doer (Doer): Optional Doer instance for the Habery. If None, it will be created based on the provided parameters.
            regery (Regery): Optional Regery instance to use. If None, it will be created based on the provided Habery.
        """
        self.name: str = name
        self.base: str = base
        self.bran: str = bran
        cf = cf if cf else habs.get_habery_configer(name=config_file, base=base, head_dir_path=config_dir)
        if hby is None and hby_doer is None:
            hby, hby_doer = habs.get_habery_and_doer(name, base, bran, cf)
        self.hby: Habery = hby
        self.rgy: Regery = regery if regery else Regery(hby=self.hby, name=self.hby.name, base=self.hby.base)
        oobiery = oobiing.Oobiery(hby=self.hby)
        self.did: str = did
        self.meta: bool = meta
        self.verbose: bool = verbose
        self.output_dir: str = output_dir

        self.did_json = {}
        self.keri_cesr = bytearray()

        self.toRemove: List[Doer] = [hby_doer] + oobiery.doers
        doers = list(self.toRemove)
        super(DIDArtifactGenerator, self).__init__(doers=doers)

    def recur(self, tock=0.0, **opts):
        """DoDoer lifecycle function that calls the underlying DID generation function. Runs once"""
        self.generate()
        return True  # run once and then stop

    def generate(self):
        """Drive did:webs did.json and keri.cesr generation"""
        logger.debug(f'\nGenerate DID doc for: {self.did}\nand metadata        : {self.meta}')
        did_json, keri_cesr = artifacting.generate_artifacts(self.hby, self.rgy, self.did, self.meta, self.output_dir)

        if self.verbose:
            print(f'keri.cesr:\n{keri_cesr.decode()}\n')
            print(f'did.json:\n{json.dumps(did_json, indent=2)}')
        self.did_json = did_json
        self.keri_cesr = keri_cesr
        self.remove(self.toRemove)
        return True
