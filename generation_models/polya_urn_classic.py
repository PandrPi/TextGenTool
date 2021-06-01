from generation_models.polya_urn import PolyaUrn


class PolyaUrnClassic(PolyaUrn):
    def __init__(self, name: str, short_name: str):
        super().__init__(name, short_name)
        self.parameters['nu'] = {'value': -1, 'constant': True}
