import os.path
from nianalysis.formats import ScanFormat
from copy import copy


class Scan(object):
    """
    A class representing either an "acquired scan", which was acquired
    externally, or a "processed scan", which was generated by a processing
    pipeline. It is also used as a placeholder in the Dataset classes to
    specify which scans (components) are expected to be provided ("acquired
    scans") or will be generated by the pipelines associated with the dataset
    ("generated scans").

    Parameters
    ----------
    name : str
        The name of the scan
    format : FileFormat
        The file format used to store the scan. Can be one of the
        recognised formats
    pipeline : Dataset.method
        The method of the dataset that is used to generate the scan. If None
        the scan is assumed to be acquired externall
    multiplicity : str
        One of 'per_subject', 'subject_subset', and 'per_project', specifying
        whether the scan is present for each subject, a subset of subjects or
        one per project.
    """

    MULTIPLICITY_OPTIONS = ('per_session', 'per_subject', 'per_project')

    def __init__(self, name, format=None, pipeline=None,  # @ReservedAssignment @IgnorePep8
                 multiplicity='per_session'):
        assert isinstance(name, basestring)
        assert isinstance(format, ScanFormat)
        assert multiplicity in self.MULTIPLICITY_OPTIONS
        self._name = name
        self._format = format
        self._pipeline = pipeline
        self._multiplicity = multiplicity
        self._prefix = ''

    def __eq__(self, other):
        return (self.name == other.name and
                self.format == other.format and
                self.pipeline == other.pipeline and
                self.multiplicity == other.multiplicity and
                self._prefix == other._prefix)

    def __ne__(self, other):
        return not (self == other)

    @property
    def name(self):
        return self._name

    @property
    def format(self):
        return self._format

    @property
    def pipeline(self):
        return self._pipeline

    @property
    def processed(self):
        return self._pipeline is not None

    @property
    def multiplicity(self):
        return self._multiplicity

    @property
    def filename(self, format=None):  # @ReservedAssignment
        if format is None:
            assert self.format is not None, "Scan format is undefined"
            format = self.format  # @ReservedAssignment
        return self._prefix + self.name + format.extension

    def match(self, filename):
        base, ext = os.path.splitext(filename)
        return base == self.name and (ext == self.format.extension or
                                      self.format is None)

    def apply_prefix(self, prefix):
        """Duplicate the scan and provide a prefix to apply to the filename"""
        duplicate = copy(self)
        duplicate._prefix = prefix
        return duplicate

    def __repr__(self):
        return ("Scan(name='{}', format={}, pipeline={})"
                .format(self.name, self.format, self.pipeline))