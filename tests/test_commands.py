import click
import pytest

import cloup


def test_group_raises_if_cls_is_not_subclass_of_cloup_Group():
    class GroupSubclass(cloup.Group):
        pass

    # Shouldn't raise with default arguments
    cloup.group('ciao')
    cloup.group(align_sections=True, cls=cloup.Group)
    cloup.group(align_sections=True, cls=GroupSubclass)
    with pytest.raises(TypeError):
        cloup.group(cls=click.Group)
