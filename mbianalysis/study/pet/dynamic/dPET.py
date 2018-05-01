from ..base import PETStudy
from nianalysis.dataset import DatasetSpec
from nianalysis.study.base import StudyMetaClass
from nipype.interfaces.fsl import ExtractROI
from nipype.interfaces.ants.resampling import ApplyTransforms
from nianalysis.interfaces.utils import Merge
from mbianalysis.interfaces.custom.pet import PETdr, GlobalTrendRemoval
from mbianalysis.data_format import (nifti_gz_format, text_matrix_format,
                                     png_format)
from nianalysis.option import OptionSpec
import os

template_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__).split('nianalysis')[0],
                 'nianalysis', 'reference_data'))


class DynamicPETStudy(PETStudy):

    __metaclass__ = StudyMetaClass

    add_data_specs = [
        DatasetSpec('pet_volumes', nifti_gz_format),
        DatasetSpec('regression_map', nifti_gz_format),
        DatasetSpec('pet_image', nifti_gz_format,
                    'Extract_vol_pipeline'),
        DatasetSpec('registered_volumes', nifti_gz_format,
                    'ApplyTransform_pipeline'),
        DatasetSpec('detrended_volumes', nifti_gz_format,
                    'Baseline_Removal_pipeline'),
        DatasetSpec('spatial_map', nifti_gz_format,
                    'Dual_Regression_pipeline'),
        DatasetSpec('ts', png_format, 'Dual_Regression_pipeline')]

    add_option_specs = [
        OptionSpec('trans_template',
                   os.path.join(template_path, 'PET_template.nii.gz')),
        OptionSpec('base_remove_th', 0),
        OptionSpec('base_remove_binarize', False),
        OptionSpec('regress_th', 0),
        OptionSpec('regress_binarize', False)]

    def Extract_vol_pipeline(self, **kwargs):
        pipeline = self.create_pipeline(
            name='Extract_volume',
            inputs=[DatasetSpec('pet_volumes', nifti_gz_format)],
            outputs=[DatasetSpec('pet_image', nifti_gz_format)],
            description=('Extract the last volume of the 4D PET timeseries'),
            version=1,
            citations=[],
            **kwargs)

        fslroi = pipeline.create_node(
            ExtractROI(roi_file='vol.nii.gz', t_min=79, t_size=1),
            name='fslroi')
        pipeline.connect_input('pet_volumes', fslroi, 'in_file')
        pipeline.connect_output('pet_image', fslroi, 'roi_file')
        return pipeline

    def ApplyTransform_pipeline(self, **kwargs):
        pipeline = self.create_pipeline(
            name='applytransform',
            inputs=[DatasetSpec('pet_volumes', nifti_gz_format),
                    DatasetSpec('warp_file', nifti_gz_format),
                    DatasetSpec('affine_mat', text_matrix_format)],
            outputs=[DatasetSpec('registered_volumes', nifti_gz_format)],
            description=('Apply transformation the the 4D PET timeseries'),
            version=1,
            citations=[],
            **kwargs)

        merge_trans = pipeline.create_node(Merge(2), name='merge_transforms')
        pipeline.connect_input('warp_file', merge_trans, 'in1')
        pipeline.connect_input('affine_mat', merge_trans, 'in2')

        apply_trans = pipeline.create_node(
            ApplyTransforms(), name='ApplyTransform')
        apply_trans.inputs.reference_image = pipeline.option(
            'trans_template')
        apply_trans.inputs.interpolation = 'Linear'
        apply_trans.inputs.input_image_type = 3
        pipeline.connect(merge_trans, 'out', apply_trans, 'transforms')
        pipeline.connect_input('pet_volumes', apply_trans, 'input_image')

        pipeline.connect_output('registered_volumes', apply_trans,
                                'output_image')
        return pipeline

    def Baseline_Removal_pipeline(self, **kwargs):

        pipeline = self.create_pipeline(
            name='Baseline_removal',
            inputs=[DatasetSpec('registered_volumes', nifti_gz_format)],
            outputs=[DatasetSpec('detrended_volumes', nifti_gz_format)],
            description=('PET dual regression'),
            citations=[],
            version=1,
            **kwargs)

        br = pipeline.create_node(GlobalTrendRemoval(),
                                  name='Baseline_removal')
        pipeline.connect_input('registered_volumes', br, 'volume')
        pipeline.connect_output('detrended_volumes', br, 'detrended_file')
        return pipeline

    def Dual_Regression_pipeline(self, **kwargs):

        pipeline = self.create_pipeline(
            name='Dual_regression',
            inputs=[DatasetSpec('detrended_volumes', nifti_gz_format),
                    DatasetSpec('regression_map', nifti_gz_format)],
            outputs=[DatasetSpec('spatial_map', nifti_gz_format),
                     DatasetSpec('ts', png_format)],
            description=('PET dual regression'),
            citations=[],
            version=1,
            **kwargs)

        dr = pipeline.create_node(PETdr(), name='PET_dr')
        dr.inputs.threshold = pipeline.option('regress_th')
        dr.inputs.binarize = pipeline.option('regress_binarize')
        pipeline.connect_input('detrended_volumes', dr, 'volume')
        pipeline.connect_input('regression_map', dr, 'regression_map')

        pipeline.connect_output('spatial_map', dr, 'spatial_map')
        pipeline.connect_output('ts', dr, 'timecourse')
        return pipeline
#     def example_pipeline_switch(self, tool='atool', **kwargs):
#         if tool == 'atool':
#             pipeline = self._atool_pipeline(**kwargs)
#         else:
#             pipeline = self._anothertool_pipeline(**kwargs)
#         return pipeline

    def dynamics_ica_pipeline(self, **kwargs):
        return self._ICA_pipeline_factory(
            input_dataset=DatasetSpec(
                'registered_volumes', nifti_gz_format, **kwargs))
