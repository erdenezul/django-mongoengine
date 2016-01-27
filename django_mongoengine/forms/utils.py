import new
from collections import OrderedDict

from django.forms.fields import Field
from django.utils import six

from document_options import DocumentMetaWrapper


def patch_document(function, instance):
    setattr(instance, function.__name__, new.instancemethod(function, instance, instance.__class__))


def init_document_options(document):
    if not hasattr(document, '_meta') or not isinstance(document._meta, DocumentMetaWrapper):
        document._admin_opts = DocumentMetaWrapper(document)
    if not isinstance(document._admin_opts, DocumentMetaWrapper):
        document._admin_opts = document._meta
    return document


def get_document_options(document):
    return DocumentMetaWrapper(document)


def get_declared_fields(bases, attrs, with_base_fields=True):
    """
    Create a list of form field instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases'). This is used by both the
    Form and ModelForm metaclasses.

    If 'with_base_fields' is True, all fields from the bases are used.
    Otherwise, only fields in the 'declared_fields' attribute on the bases are
    used. The distinction is useful in ModelForm subclassing.
    Also integrates any additional media definitions.
    """

    fields = [
        (field_name, attrs.pop(field_name))
        for field_name, obj in list(six.iteritems(attrs)) if isinstance(obj, Field)
    ]
    fields.sort(key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                fields = list(six.iteritems(base.base_fields)) + fields
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_fields'):
                fields = list(six.iteritems(base.declared_fields)) + fields

    return OrderedDict(fields)
