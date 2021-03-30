from generation_models.polya_urn import PolyaUrn


class PolyaUrnClassic(PolyaUrn):
    def __init__(self, name: str):
        super().__init__(name)
        self.parameters['nu'] = {'value': -1, 'constant': True}
