# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     J.L. Vilas (jlvilas@cnb.csic.es),
#                Y.C. Fonseca Reyna (cfonseca@cnb.csic.es )
# *
# * your institution
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************
import logging
import os
from collections import OrderedDict

import emtable
from pwem.protocols import EMProtocol
from pyworkflow.constants import BETA
from pyworkflow.protocol import params
from pyworkflow.utils import removeBaseExt

from tomo.objects import Tomogram
from tomo.protocols import ProtTomoBase
from ..constants import *
from isonet import Plugin


class ProtIsoNetTomoReconstruction(EMProtocol, ProtTomoBase):
    """
     Isotropic Reconstruction of Electron Tomograms with Deep Learning
    """
    _label = 'tomo reconstruction'
    _devStatus = BETA

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection(label='Input')

        form.addParam('inputTomograms', params.PointerParam, pointerClass='SetOfTomograms',
                      label="Tomograms", important=True,
                      help='Select the input tomogram for restoring the missing wedge.')

        form.addParam('inputSetOfCtfTomoSeries', params.PointerParam,
                      allowsNull=True,
                      label="CTF tomo series",
                      pointerClass='SetOfCTFTomoSeries',
                      help='Select the CTF estimation for the set '
                           'of tilt-series.')

        form.addParam('snrfalloff', params.FloatParam, default=1.0,
                      condition='inputSetOfCtfTomoSeries is not None',
                      label="SNR fall rate",
                      help='SNR fall rate with the frequency. High values means losing more high frequency.'
                           'If this value is not set, the program will look for the parameter in the star file.'
                           'If this value is not set and not found in star file, the default value 1.0 will be used.')

        form.addParam('deconvstrength', params.FloatParam, default=1.0,
                      condition='inputSetOfCtfTomoSeries is not None',
                      label="Strength of the deconvolution",
                      help='SNR fall rate with the frequency. High values means losing more high frequency.'
                           'If this value is not set, the program will look for the parameter in the star file.'
                           'If this value is not set and not found in star file, the default value 1.0 will be used.')

        form.addParam('highpassnyquist', params.FloatParam, default=0.02,
                      condition='inputSetOfCtfTomoSeries is not None',
                      label="Highpass filter",
                      help='Highpass filter for at very low frequency. We suggest to keep this default value.')

        form.addParam('chunk_size', params.FloatParam, default=None,
                      condition='inputSetOfCtfTomoSeries is not None',
                      allowsNull=True,
                      label="The overlapping rate",
                      help='The overlapping rate for adjecent chunks.')

        form.addParam('overlap_rate', params.FloatParam, default=None,
                      condition='inputSetOfCtfTomoSeries is not None',
                      allowsNull=True,
                      label="Highpass filter",
                      help='Highpass filter for at very low frequency. We suggest to keep this default value.')

        form.addParam('generateMask', params.BooleanParam, default=True,
                      label="Generate mask?",
                      help='Generate a mask that include sample area and exclude "empty" area of the tomogram. '
                           'The masks do not need to be precise. In general, the number of '
                           'subtomograms (a value in star file) should be lesser if you masked out larger area.')

        form.addParam('patch_size', params.IntParam, default=4,
                      condition="generateMask==%d" % True,
                      label="Patch size",
                      help=' The size of the box from which the max-filter and std-filter are calculated.')
        form.addParam('density_percentage', params.IntParam, default=50,
                      condition="generateMask==%d" % True,
                      label="Density percentage",
                      help='The approximate percentage of pixels to keep based on their local pixel density.'
                           'If this value is not set, the program will look for the parameter in the star file.'
                           'If this value is not set and not found in star file, the default value 50 will be used.')
        form.addParam('std_percentage', params.IntParam, default=50,
                      condition="generateMask==%d" % True,
                      label="Std percentage",
                      help='The approximate percentage of pixels to keep based on their local standard deviation.'
                            'If this value is not set, the program will look for the parameter in the star file.'
                            'If this value is not set and not found in star file, the default value 50 will be used.')

        form.addParam('z_crop', params.FloatParam, default=0.2,
                      condition="generateMask==%d" % True,
                      label="Z_crop",
                      help='If exclude the top and bottom regions of tomograms along z axis. '
                           'For example, "0.2" will mask out the top 20% and bottom 20% region along z axis.')

        form.addParam('tomo_idx', params.StringParam, default=None,
                      condition="generateMask==%d" % True,
                      label="Tomo index",
                      help=' If this value is set, process only the tomograms listed in this index. e.g. 1,2,4 or 5-10,15,16')

        form.addSection("Extract subtomograms")
        form.addParam('number_subtomos', params.IntParam, default=100,
                      label="Number of subtomograms to be extracted per tomogram",
                      help='Number of subtomograms to be extracted')
        form.addParam('cube_size', params.IntParam, default=8,
                      allowsNull=True,
                      label="Size of cubes",
                      help='Size of cubes for training, should be divisible by 8, eg. 32, 64. '
                           'The actual sizes of extracted subtomograms are this value adds 16.'
                           'This is the size of the cubic volumes used for training. This values should be smaller than the size of subtomogram. '
                           'And the cube_size should be divisible by 8. If this value isnt '
                           'set, cube_size is automatically determined as int(subtomo_size / 1.5 + 1)//16 * 16')

        form.addParam('crop_size', params.IntParam, default=24,
                      allowsNull=True,
                      label="Crop size",
                      help='The size of subtomogram, should be larger than the '
                           'cube_size The default value should be 16+cube_size.')

        form.addSection("Training settings")

        form.addParam('pretrained_model', params.PathParam,
                      label="Training model path",
                      help='A trained neural network model in ".h5" format to start with.')
        form.addParam('iterations', params.IntParam, default=30,
                      label='Number of training iterations',
                      help='Number of training iterations')

        form.addParam('epochs', params.IntParam, default=10,
                      label='Number of epoch',
                      help='Number of epoch for each iteraction')
        form.addParam('batch_size', params.IntParam, default=None,
                       label='Batch size',
                       allowsNull=True,
                       help='Size of the minibatch.If None, batch_size will be '
                            'the max(2 * number_of_gpu,4). batch_size should be '
                            'divisible by the number of gpu.')
        form.addParam('steps_per_epoch', params.IntParam, default=None,
                       label='Steps per epoch',
                       allowsNull=True,
                       help='Step per epoch. If not defined, the default'
                            ' value will be min(num_of_subtomograms * 6 / batch_size , 200')

        form.addSection("Denoise settings")
        form.addParam('noise_level', params.StringParam, default='0.05,0.1,0.15,0.2',
                       label='Level of noise',
                       help='Level of noise STD(added noise)/STD(data) after '
                            'the iteration defined in noise_start_iter.')
        form.addParam('noise_start_iter', params.StringParam, default='11,16,21,26',
                       label='Noise start iter',
                       help='Iteration that start to add noise of corresponding noise level.')

        form.addParam('noise_mode', params.EnumParam,
                      choices=['ramp', 'hamming', 'noFilter'],
                      important=True,
                      display=params.EnumParam.DISPLAY_COMBO,
                      default=2,
                      label="Filter names",
                      help="Filter names when generating noise volumes, can be 'ramp', 'hamming' and 'noFilter'"
                      )

        form.addSection("Network settings")
        form.addParam('drop_out', params.FloatParam,
                       default=0.3,
                       label='Drop out rate',
                       help='Drop out rate to reduce overfitting')
        form.addParam('learning_rate', params.FloatParam,
                       default=0.0004,
                       label='Learning rate',
                       help='Learning rate for network training.')
        form.addParam('convs_per_depth', params.IntParam,
                       default=3,
                       label='Number of convolution layer',
                       help='Number of convolution layer for each depth')
        form.addParam('unet_depth', params.IntParam,
                       default=3,
                       label='Depth of UNet',
                       help='Depth of UNet.')
        form.addParam('kernel', params.StringParam,
                      default="3,3,3",
                      label='Kernel for convolution',
                      help='Kernel for convolution')
        form.addParam('filter_base', params.IntParam,
                       default=64,
                       label='Filter base',
                       help='The base number of channels after convolution.')
        form.addParam('batch_normalization', params.BooleanParam,
                       default=True,
                       label='Use batch normalization layer?',
                       help='Use Batch Normalization layer')
        form.addParam('pool', params.BooleanParam,
                       default=False,
                       label='Use pooling layer?',
                       help='Use pooling layer instead of stride convolution layer')
        form.addParam('normalize_percentile', params.BooleanParam,
                       default=True,
                       label='Normalize percentile?',
                       help='Normalize the 5 percent and 95 percent pixel '
                            'intensity to 0 and 1 respectively. If this is set '
                            'to False, normalize the input to 0 mean and 1 '
                            'standard deviation.')


        form.addParallelSection(threads=0, mpi=1)
        form.addParam(params.GPU_LIST, params.StringParam, default='0',
                       label='Choose GPU IDs:', validators=[params.NonEmpty],
                       help='This argument is necessary. By default, the '
                            'protocol will attempt to launch on GPU 0. You can '
                            'override the default allocation by providing a '
                            'list of which GPUs (0,1,2,3, etc) to use. '
                            'GPU are separated by ",". For example: "0,1,5"')

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        self.tomoPath = os.path.abspath(self._getExtraPath(TOMOGRAMFOLDER))
        self.tomoStarFileName = os.path.join(self.tomoPath, OUTPUT_TOMO_STAR_FILE)
        self.maskPath = os.path.abspath(os.path.join(self.tomoPath, MASKFOLDER))
        self.deconvFolder = os.path.abspath(os.path.join(self.tomoPath, DECONVFOLDER))
        self.subtomoPath = os.path.abspath(os.path.join(self.tomoPath, SUBTOMOGRAMFOLDER))
        self.subtomoStarFile = os.path.abspath(os.path.join(self.tomoPath, OUTPUT_SUBTOMO_STAR_FILE))
        self.resultsFolder = os.path.join(self.tomoPath, RESULTFOLDER)
        self.predictFolder = os.path.join(self.tomoPath, PREDICTEDFOLDER)

        self._insertFunctionStep(self.prepareProjectStep)
        if self.inputSetOfCtfTomoSeries.get() is not None:
            self._insertFunctionStep(self.ctfDeconvolveStep)
        if self.generateMask.get():
            self._insertFunctionStep(self.generateMaskStep)
        self._insertFunctionStep(self.extractSubtomogramsStep)
        self._insertFunctionStep(self.refineStep)
        self._insertFunctionStep(self.predictStep)
        self._insertFunctionStep(self.createOutputStep)

    def prepareProjectStep(self):
        """
        Generates a subtomo star file from a set of subtomogram (.mrc)
        """
        if not os.path.exists(self.tomoPath):
            os.mkdir(self.tomoPath)
        for tomo in self.inputTomograms.get():
            tomofn = os.path.abspath(tomo.getFileName())
            tomoName = tomo.getTsId()
            tomoLnName = os.path.join(self.tomoPath, tomoName + '.mrc')
            if not os.path.exists(tomoLnName):
                os.link(tomofn, tomoLnName)

        pixel_size = self.inputTomograms.get().getSamplingRate()

        args = '%s --output_star %s --pixel_size %f --defocus %f --number_subtomos %d' \
               %(self.tomoPath, self.tomoStarFileName, pixel_size, 0.0,
                 self.number_subtomos.get())

        Plugin.runIsoNet(self, Plugin.getProgram(PROGRAM_PREPARE_STAR), args=args)

    def ctfDeconvolveStep(self):
        """
        CTF deconvolution for the tomograms.

        isonet.py deconv star_file [--deconv_folder] [--snrfalloff] [--deconvstrength] [--highpassnyquist] [--overlap_rate] [--ncpu] [--tomo_idx]
        This step is recommanded because it enhances low resolution information for a better contrast. No need to do deconvolution for phase plate data.
        """
        if not os.path.exists(self.deconvFolder):
            os.mkdir(self.deconvFolder)
        mdFile = emtable.Table(fileName=self.tomoStarFileName, tableName=None)
        tomoRow = OrderedDict()
        newStarFile = os.path.abspath(os.path.join(self.tomoPath, OUTPUT_TOMO_DECONV_STAR_FILE))
        defocusValues = self.getDefocusValues()
        with open(newStarFile, 'w') as f:
            # Write particles table
            f.write("# Star file generated with Scipion\n")
            f.write("# version 30001\n")
            # Write header first
            partsWriter = emtable.Table.Writer(f)
            partsWriter.writeTableName('particles')
            partsWriter.writeHeader(mdFile.getColumns())
            # Write all rows
            for index, row in enumerate(mdFile.iterRows(fileName=self.tomoStarFileName)):
                tomoRow['rlnIndex'] = row.get('rlnIndex')
                tomoRow['rlnMicrographName'] = row.get('rlnMicrographName')
                tomoRow['rlnPixelSize'] = row.get('rlnPixelSize')
                tomoName = removeBaseExt(tomoRow['rlnMicrographName'])
                tomoRow['rlnDefocus'] = defocusValues[tomoName]
                tomoRow['rlnNumberSubtomo'] = row.get('rlnNumberSubtomo')
                tomoRow['rlnMaskBoundary'] = row.get('rlnMaskBoundary')
                partsWriter.writeRowValues(tomoRow.values())

        mdFile.write(self.tomoStarFileName)
        os.system(f'mv {newStarFile} {self.tomoStarFileName}')

        args = '%s --deconv_folder %s --snrfalloff %f --deconvstrength %d --highpassnyquist %f --ncpu %d ' \
               % (self.tomoStarFileName,
                  self.deconvFolder,
                  self.snrfalloff.get(),
                  self.deconvstrength.get(),
                  self.highpassnyquist.get(),
                  self.numberOfMpi.get())

        chunk_size = self.chunk_size.get()
        if chunk_size is not None:
            args += '--chunk_size %d ' % chunk_size

        overlap_rate = self.overlap_rate.get()
        if overlap_rate is not None:
            args += '--overlap_rate %d ' % overlap_rate

        if self.tomo_idx.get() is not None:
            args += ' --tomo_idx %s' % self.tomo_idx.get()

        Plugin.runIsoNet(self, Plugin.getProgram(PROGRAM_CTF_DECONV), args=args)

    def getDefocusValues(self):
        defocusValues = dict()
        setOfCtfTomoSeries = self.inputSetOfCtfTomoSeries.get()
        half = 0
        for tiltSerie in setOfCtfTomoSeries.getSetOfTiltSeries().getFirstItem():
            half += 1
            if tiltSerie.getTiltAngle() == 0:
                break
        for ctfTomoSerie in setOfCtfTomoSeries.iterItems():
                defocusValues[ctfTomoSerie.getTsId()] = ctfTomoSerie[half].getDefocusU()
        return defocusValues

    def generateMaskStep(self):
        """
        Generate a mask that include sample area and exclude empty area of
        the tomogram. The masks do not need to be precise. In general,
        the number of subtomograms (a value in star file) should be lesser if
        you masked out larger area."
        "make_mask star_file [--mask_folder] [--patch_size] [--density_percentage] [--std_percentage] [--use_deconv_tomo] [--tomo_idx]"
        """

        if not os.path.exists(self.maskPath):
            os.mkdir(self.maskPath)
        args = '%s --mask_folder %s --patch_size %d --density_percentage %d --std_percentage %d --z_crop %f' \
               % (self.tomoStarFileName, self.maskPath,
                  self.patch_size.get(),
                  self.density_percentage.get(),
                  self.std_percentage.get(),
                  self.z_crop.get())

        if self.inputSetOfCtfTomoSeries.get() is not None:
            args += ' --use_deconv_tomo True'

        if self.tomo_idx.get() is not None:
            args += ' --tomo_idx %s' % self.tomo_idx.get()

        Plugin.runIsoNet(self, Plugin.getProgram(PROGRAM_GENERATE_MASK),
                         args=args)

    def extractSubtomogramsStep(self):
        """
        Extract subtomograms
        extract star_file [--subtomo_folder] [--subtomo_star] [--cube_size] [--use_deconv_tomo] [--crop_size] [--tomo_idx]
        """
        if not os.path.exists(self.subtomoPath):
            os.mkdir(self.subtomoPath)
        args = '%s --subtomo_folder %s --subtomo_star %s ' \
               % (self.tomoStarFileName, self.subtomoPath, self.subtomoStarFile)

        cube_size = self.cube_size.get()
        if cube_size is None:
            cube_size = 8
            logging.info("Setting cube_size parameter to %d" % cube_size)
        args += '--cube_size %d ' % cube_size


        crop_size = self.crop_size.get()
        if crop_size is None:
            crop_size = cube_size + 16
            logging.info("Setting crop_size parameter to %d" % crop_size)
        args += '--crop_size %d ' % crop_size


        if self.inputSetOfCtfTomoSeries.get() is not None:
            args += ' --use_deconv_tomo True '

        if self.tomo_idx.get() is not None:
            args += ' --tomo_idx %s' % self.tomo_idx.get()

        Plugin.runIsoNet(self, Plugin.getProgram(PROGRAM_EXTRACT_SUBTOMOGRAMS),
                         args=args)

    def refineStep(self):
        """
        Train neural network to correct missing wedge

        isonet.py refine subtomo_star [--iterations] [--gpuID] [--preprocessing_ncpus] [--batch_size] [--steps_per_epoch] [--noise_start_iter] [--noise_level]...
        """
        args = '%s --iterations %d --epochs %d --gpuID %s --preprocessing_ncpus %d --noise_level %s ' \
               '--noise_start_iter %s --drop_out %f --learning_rate %f ' \
               '--convs_per_depth %d --unet_depth %d --filter_base %d --kernel %s --result_dir %s ' \
               % (self.subtomoStarFile,
                  self.iterations.get(),
                  self.epochs.get(),
                  str(self.getGpuList())[1:-1].replace(' ', ''),
                  self.numberOfMpi.get(),
                  self.noise_level.get(),
                  self.noise_start_iter.get(),
                  self.drop_out.get(),
                  self.learning_rate.get(),
                  self.convs_per_depth.get(),
                  self.unet_depth.get(),
                  self.filter_base.get(),
                  self.kernel.get(),
                  self.resultsFolder)

        if self.pool.get() is True:
            args += '--pool True '

        if self.batch_normalization.get() is False:
            args += '--batch_normalization False '

        if self.normalize_percentile.get() is False:
            args += '--normalize_percentile False '

        noise_mode = self.noise_mode.get()
        if noise_mode != 2:
            args += '--noise_mode %s ' % NOISE_MODE[noise_mode]

        pretrained_model = self.pretrained_model.get()
        if pretrained_model is not None:
            args += '--pretrained_model %s ' % pretrained_model

        batch_size = self.batch_size.get()
        if batch_size is None:
            batch_size = max(2*len(self.getGpuList()), 4)
        steps_per_epoch = self.steps_per_epoch.get()

        if steps_per_epoch is None:
            steps_per_epoch = min(self.number_subtomos.get() * 6 / batch_size, 200)

        args += ' --batch_size %d --steps_per_epoch %d' % (batch_size, steps_per_epoch)
        Plugin.runIsoNet(self, Plugin.getProgram(PROGRAM_REFINE),
                         args=args)

    def predictStep(self):
        """
         Predict tomograms using trained model
        isonet.py predict star_file model [--gpuID] [--output_dir] [--cube_size] [--crop_size] [--batch_size] [--tomo_idx]
        """
        if not os.path.exists(self.predictFolder):
            os.mkdir(self.predictFolder)
        modelName = getTrinedModelName(self.iterations.get())
        modelPath = os.path.join(self.resultsFolder, modelName)
        batch_size = self.batch_size.get()
        if batch_size is None:
            batch_size = max(2 * len(self.getGpuList()), 4)

        args = '%s %s --gpuID %s --batch_size %d --output_dir %s ' \
               % (self.tomoStarFileName,
                  modelPath,
                  str(self.getGpuList())[1:-1].replace(' ', ''),
                  batch_size,
                  self.predictFolder)

        cube_size = self.cube_size.get()
        if cube_size is None:
            cube_size = 8
            logging.info("Setting cube_size parameter to %d" % cube_size)
        args += '--cube_size %d ' % cube_size

        crop_size = self.crop_size.get()
        if crop_size is None:
            crop_size = cube_size + 16
            logging.info("Setting crop_size parameter to %d" % crop_size)
        args += '--crop_size %d ' % crop_size

        tomo_idx = self.tomo_idx.get()
        if tomo_idx is not None:
            args += '--tomo_idx %s ' % tomo_idx

        if self.inputSetOfCtfTomoSeries.get() is not None:
            args += '--use_deconv_tomo True'

        Plugin.runIsoNet(self, Plugin.getProgram(PROGRAM_PREDICT),
                         args=args)

    def createOutputStep(self):
        samplingRate = self.inputTomograms.get().getSamplingRate()
        tomoSet = self._createSetOfTomograms()
        tomoSet.setSamplingRate(samplingRate)
        tomograms = os.listdir(self.predictFolder)

        for fileName in tomograms:
            tomo = Tomogram()
            tomo.setSamplingRate(samplingRate)
            tomoId = fileName
            tomo.cleanObjId()
            tomo.setTsId(tomoId)
            location = os.path.join(self.predictFolder, fileName)
            tomo.setLocation(location)
            tomo.setOrigin()
            tomoSet.append(tomo)

        self._defineOutputs(outputTomograms=tomoSet)

    def _validate(self):
        msg =[]
        cube_size = self.cube_size.get()
        if cube_size is not None and cube_size % 8 != 0:
            msg.append("The size of cubes parameter(Extract subtomogram tab) "
                       "must be a multiple of 8")
        return msg

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []
        return summary

    def _methods(self):
        methods = []
        return methods
