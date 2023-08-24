import unittest
from .point_description import AnchorPoint


class TestPointDescription(unittest.TestCase):
    def setUp(self) -> None:
        self.anchor_point = AnchorPoint()

    def test_set_name_submodel(self):
        self.anchor_point.full_description_of_the_submodel = ['sdawdqd']
        self.assertEquals(self.anchor_point.set_name_submodel(), None)

        self.anchor_point.full_description_of_the_submodel = ['xlink:href="Ds_ana.svg"']
        self.assertEquals(self.anchor_point.set_name_submodel(), self.anchor_point.name_submodel == 'Ds_ana.svg')

    def test_set_width_and_height(self):
        self.anchor_point.full_description_of_the_submodel = ['width="75" and height="50"']
        self.assertEquals(self.anchor_point.set_width_and_height(),
                          self.anchor_point.width == 75,
                          self.anchor_point.height == 50)

        self.anchor_point.full_description_of_the_submodel = ['and height="50"']
        self.assertEquals(self.anchor_point.set_width_and_height(), None)


if __name__ == '__main__':
    unittest.main()
