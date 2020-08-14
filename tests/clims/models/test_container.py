from __future__ import absolute_import

import re
import uuid
import pytest
from six import text_type
from sentry.testutils import TestCase
from clims.services import SubstanceBase
from clims.services.container import PlateBase
from clims.services import FloatField, TextField
from clims.models import Container
from django.db import IntegrityError


class TestContainer(TestCase):
    def setUp(self):
        self.register_extensible(HairSampleContainer)
        self.register_extensible(HairSample)
        self.has_context()

    def test_can_register_container(self):
        self.register_extensible(HairSampleContainer)

    def test_can_create_container(self):
        self.register_extensible(HairSampleContainer)
        container = HairSampleContainer(name="container1")
        container.save()
        Container.objects.get(name=container.name)  # Raises DoesNotExist if it wasn't created

    def test_name_is_unique(self):
        self.register_extensible(HairSampleContainer)
        container = HairSampleContainer(name="container1")
        container.save()
        container2 = HairSampleContainer(name=container.name)
        with pytest.raises(IntegrityError):
            container2.save()

    @pytest.mark.dev_edvard
    def test_can_add_custom_property(self):
        self.register_extensible(HairSampleContainer)
        container = HairSampleContainer(name="container1")
        container.comment = "test"
        container.save()

        container_fetched_again = self.app.containers.get(id=container.id)
        assert container.comment == container_fetched_again.comment

    def test_can_add_sample(self):
        self.register_extensible(HairSampleContainer)
        self.register_extensible(HairSample)

        sample = HairSample(name="sample1")
        sample.length = 10
        sample.width = 20

        from clims.models import Substance
        container = HairSampleContainer(name="container1")
        container.comment = "This container is great and live is awesome"
        container["A1"] = sample

        # NOTE: This will also save all the samples in the container
        container.save()

        model = Substance.objects.get(name='sample1')
        location = model.locations.get(current=True)
        assert (location.x, location.y, location.z) == (0, 0, 0)

    def test_can_traverse_plate(self):
        container = self.create_container_with_samples(HairSampleContainer, HairSample, sample_count=3)

        # container = HairSampleContainer(name="cont1")
        by_row = list(container._traverse(HairSampleContainer.TRAVERSE_BY_ROW))
        by_col = list(container._traverse(HairSampleContainer.TRAVERSE_BY_COLUMN))

        assert len(by_row) == 8 * 12
        assert len(by_col) == 8 * 12

        assert ([text_type(x) for x in by_row[0:13]]
                == ['A:1', 'A:2', 'A:3', 'A:4', 'A:5', 'A:6', 'A:7',
                    'A:8', 'A:9', 'A:10', 'A:11', 'A:12', 'B:1'])
        assert ([text_type(x) for x in by_col[0:13]]
                == ['A:1', 'B:1', 'C:1', 'D:1', 'E:1', 'F:1', 'G:1', 'H:1',
                    'A:2', 'B:2', 'C:2', 'D:2', 'E:2'])

    def test_can_address_plate_with_zero_based_row_col(self):
        self.register_extensible(HairSampleContainer)
        self.register_extensible(HairSample)

        container = HairSampleContainer(name="cont-{}".format(uuid.uuid4()))
        sample = HairSample(name="sample-{}".format(container.name))

        container["A:1"] = sample
        container.save()
        assert container[(0, 0)] == container["A:1"]
        assert container["A:1"] == sample

    @pytest.mark.dev_edvard
    def test_can_address_plate_with_plate_index(self):
        self.register_extensible(HairSampleContainer)
        self.register_extensible(HairSample)

        container = HairSampleContainer(name="cont-{}".format(uuid.uuid4()))
        sample = HairSample(name="sample-{}".format(container.name))

        container["A:1"] = sample
        container.save()
        assert container[sample.location] == sample

    def test_can_add_samples_without_location(self):
        # Ensure one can just append directly to the container, like if it were a list
        # The order is specific to the particular container being used, but since
        # HairSampleContainer doesn't override the default, it uses TRAVERSE_BY_COLUMN, i.e. it
        # fills a column before it goes to the next column.

        container = HairSampleContainer(name="cont-{}".format(uuid.uuid4()))

        in_original_order = list()
        for ix in range(2):
            sample = HairSample(name="sample-{}-{}".format(container.name, ix))
            in_original_order.append(sample)
            container.append(sample)
        container.save()
        assert container["A:1"].id == in_original_order[0].id

        container_fresh = self.app.containers.get_by_name(container.name)
        assert container_fresh["A:1"].id == in_original_order[0].id

    def test_can_output_default_string_info(self):
        # One should be able to get a detailed text version of the container for debugging
        # and demoing.
        container = HairSampleContainer(name="cont-{}".format(uuid.uuid4()))

        for ix in range(container.rows):
            sample = HairSample(name="sample-{}-{}".format(container.name, ix))
            container.append(sample)
        container.save()

        container_fresh = self.app.containers.get_by_name(container.name)
        string_rep = container_fresh.to_string().split("\n")
        assert len(string_rep) == container.rows

        first_line = string_rep[0].strip()

        # Expecting a digit followed by some empty columns:
        assert re.match(r"^\d+[ |].+", first_line) is not None

    @pytest.mark.skip('This feature is not currently working')
    def test_get_container_from_sample__when_container_is_unregisterred__container_reference_still_works(self):
        container = HairSampleContainer(name="cont-{}".format(uuid.uuid4()))

        sample = HairSample(name="sample-{}-{}".format(container.name, uuid.uuid4()))
        # container.append(sample)
        container['B2'] = sample
        container.save()
        self.app.extensibles.unregister_model(HairSampleContainer, self.create_plugin())
        fresh_sample = self.app.substances.get_by_name(sample.name)

        # Act
        container_index = fresh_sample.location

        # Assert

        assert container_index.x == 1
        assert container_index.y == 1
        assert container_index.z is None

    # TODO: Test that ensures that all samples have the container, perhaps
    # reusing the container domain object if in the same context (e.g. in a handler)


class HairSampleContainer(PlateBase):
    rows = 8
    columns = 12

    comment = TextField("comment")


class HairSample(SubstanceBase):
    length = FloatField("length")
    width = FloatField("width")
