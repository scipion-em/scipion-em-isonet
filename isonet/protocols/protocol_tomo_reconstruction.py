# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     J.L. Vilas (jlvilas@cnb.csic.es)
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


"""
Describe your python module here:
This module will provide the traditional Hello world example
"""
import os

from pyworkflow.constants import BETA
from pyworkflow.protocol import Protocol, params, Integer
from pyworkflow.utils import Message
from pyworkflow.protocol.params import (PointerParam, BooleanParam, FloatParam,
                                        LEVEL_ADVANCED)


class ProtIsoNetTomoReconstruction(Protocol):
    """
     Isotropic Reconstruction of Electron Tomograms with Deep Learning
    """
    _label = 'isonet tomo reconstruction'
    _devStatus = BETA

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection(label='Input')

        form.addParam('inputTomograms', PointerParam, pointerClass='SetOfTomograms',
                      label="Odd tomogram", important=True,
                      help='Select the input tomogram for restoring the missing wedge.')

        form.addParam('useMask', BooleanParam, default=False,
                      label="Use mask?",
                      help='The mask determines which points are specimen'
                           ' and which are not.')

        form.addParam('Mask', PointerParam, pointerClass='VolumeMask',
                      condition='useMask', allowsNull=True,
                      label="Binary Mask",
                      help='The mask determines which points are specimen'
                           ' and which are not')

        form.addParam('ctfDeconv', BooleanParam, default=True,
                      label="Apply CTF deconvolution?",
                      help='Apply CTF deconvolution.')

        group = form.addGroup('Extra parameters')
        line = group.addLine('Resolution Range (Å)',
                             help="Resolution range (and step in expert mode) "
                                  "to analyze the local resolution.")

        group.addParam('significance', FloatParam, default=0.95,
                       expertLevel=LEVEL_ADVANCED,
                       label="Significance",
                       help='Relution is computed using hypothesis tests, '
                            'this value determines the significance of that test')

        line.addParam('minRes', FloatParam, default=0, label='High')
        line.addParam('maxRes', FloatParam, allowsNull=True, label='Low')
        line.addParam('stepSize', FloatParam, allowsNull=True, default=0.5,
                      expertLevel=LEVEL_ADVANCED, label='Step')

        form.addSection("Computing")
        form.addParam('batchSize', params.IntParam, default=4,
                      label='Batch Size',
                      help='This value allows to group several items to be processed inside the same protocol step.'
                           'Specify a smaller batch_size or use more(powerful) GPUs. '
                           'The default batch_size is 4 if you use one GPU, '
                           'otherwise the default batch_size is 2 times the number of GPU. '
                           'Please note the batch_size should be divisiable by number of GPUs. '
                           'For example, if you have one GPU and get OOM error, please reduce '
                           'the batch_size to 1 or 2; If you use 4 GPUs and get OOM error, '
                           'please reduce the batch_size to 4')

        form.addParallelSection(threads=4, mpi=0)

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        for tomo in self.inputTomograms.get():
            tomId = tomo.getObjId()
            self._insertFunctionStep('prepareProjectStep', tomId)
            if self.ctfDeconv.get():
                self._insertFunctionStep('ctfDeconvolveStep', tomId)
            self._insertFunctionStep('extractSubtomogramsStep')
            self._insertFunctionStep('refineStep')
            self._insertFunctionStep('predictStep')
        self._insertFunctionStep('createOutputStep')

    def prepareProjectStep(self, tomId):
        pass

    def ctfDeconvolveStep(self):
        pass

    def extractSubtomogramsStep(self):
        pass

    def refineStep(self):
        pass

    def predictStep(self):
        pass

    def createOutputStep(self):
       pass

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []
        return summary

    def _methods(self):
        methods = []
        return methods
