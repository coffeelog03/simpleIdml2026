# -*- coding: utf-8 -*-

import os
import shutil
from tempfile import NamedTemporaryFile


def simple_decorator(decorator):
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator


@simple_decorator
def use_working_copy(view_func):
    def new_func(idml_package, *args, **kwargs):
        if idml_package.working_copy_path is not None:
            return view_func(idml_package, *args, **kwargs)

        tmp_filename = NamedTemporaryFile().name
        idml_package.extractall(tmp_filename)
        idml_package.working_copy_path = tmp_filename
        idml_package.init_lazy_references()

        if idml_package.debug:
            # In debug it is useful to have the original trace.
            idml_package = view_func(idml_package, *args, **kwargs)
        else:
            # Catch any exception to reset working_copy_path.
            try:
                idml_package = view_func(idml_package, *args, **kwargs)
            except BaseException as err:
                idml_package.working_copy_path = None
                raise err

        # Create a new archive from the extracted one.
        # Use the newly added _repack method in IDMLPackage
        tmp_package_filename = f"{tmp_filename}.idml"
        idml_package._repack(tmp_package_filename)

        # swap working_copy with initial IDML Package.
        new_filename = idml_package.filename
        idml_package.close()
        os.unlink(idml_package.filename)
        shutil.move(tmp_package_filename, new_filename)
        shutil.rmtree(tmp_filename)
        idml_package.working_copy_path = None
        
        from simple_idml.idml import IDMLPackage  # pylint: disable=import-outside-toplevel
        return IDMLPackage(new_filename)

    return new_func
