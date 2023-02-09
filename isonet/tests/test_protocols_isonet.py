# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
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

import os

from pyworkflow.tests import setupTestProject, BaseTest, DataSet
from pwem.emlib.image import ImageHandler
import tomo.protocols
import imod.protocols

DataSet(name='novaCtfTestData',
        folder='novaCtfTestData',
        files={
            'tsCtf': 'tomo1_bin4.mrc'})

from ..protocols import *



class TestIsoNetCtfBase(BaseTest):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)

    @classmethod
    def _runImportTiltSeries(cls, filesPath, pattern, voltage, magnification,
                             samplingRate, dosePerFrame, anglesFrom=0, minAngle=0.0, maxAngle=0.0,
                             stepAngle=1.0, tiltAxisAngle=0.0):
        cls.protImportTS = cls.newProtocol(tomo.protocols.ProtImportTs,
                                           filesPath=filesPath,
                                           filesPattern=pattern,
                                           voltage=voltage,
                                           anglesFrom=anglesFrom,
                                           magnification=magnification,
                                           samplingRate=samplingRate,
                                           dosePerFrame=dosePerFrame,
                                           minAngle=minAngle,
                                           maxAngle=maxAngle,
                                           stepAngle=stepAngle,
                                           tiltAxisAngle=tiltAxisAngle)

        cls.launchProtocol(cls.protImportTS)

        return cls.protImportTS

    @classmethod
    def _runImodCTFEstimation(cls, inputSoTS, expectedDefocusOrigin, angleRange,
                          expectedDefocusValue, searchAstigmatism):
        cls.protCTFEstimation = cls.newProtocol(imod.protocols.ProtImodAutomaticCtfEstimation,
                                                inputSet=inputSoTS,
                                                expectedDefocusOrigin=expectedDefocusOrigin,
                                                expectedDefocusValue=expectedDefocusValue,
                                                angleRange=angleRange,
                                                searchAstigmatism=searchAstigmatism)

        cls.launchProtocol(cls.protCTFEstimation)

        return cls.protCTFEstimation

    @classmethod
    def _runComputeCtfArray(cls, inputSetOfTiltSeries, inputSetOfCtfTomoSeries, tomoThickness, tomoShift,
                            defocusStep, correctionType, correctAstigmatism):
        cls.protCTFReconstruction = cls.newProtocol(ProtNovaCtfTomoDefocus,
                                                    inputSetOfTiltSeries=inputSetOfTiltSeries,
                                                    inputSetOfCtfTomoSeries=inputSetOfCtfTomoSeries,
                                                    tomoThickness=tomoThickness,
                                                    tomoShift=tomoShift,
                                                    defocusStep=defocusStep,
                                                    correctionType=correctionType,
                                                    correctAstigmatism=correctAstigmatism)

        cls.launchProtocol(cls.protCTFReconstruction)

        return cls.protCTFReconstruction


class TestIsoNetReconstructionWorkflow(TestIsoNetCtfBase):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)

        cls.inputDataSet = DataSet.getDataSet('novaCtfTestData')
        cls.inputSoTS = cls.inputDataSet.getFile('tsCtf')

        cls.protImportTS = cls._runImportTiltSeries(
            filesPath=os.path.dirname(cls.inputSoTS),
            pattern="tomo1_bin4.mrc",
            anglesFrom=0,
            voltage=300,
            magnification=50000,
            samplingRate=8.8,
            dosePerFrame=0.3,
            minAngle=-60.0,
            maxAngle=60.0,
            stepAngle=3.0,
            tiltAxisAngle=2.8)

        cls.protCTFEstimation = cls._runImodCTFEstimation(
            inputSoTS=cls.protImportTS.outputTiltSeries,
            expectedDefocusOrigin=0,
            expectedDefocusValue=6000,
            angleRange=20,
            searchAstigmatism=0)


    def test_tomoReconstructionOutput(self):
       pass