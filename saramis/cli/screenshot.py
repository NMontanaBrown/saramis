# coding=utf-8

"""
Slicer script for extracting the skeleton of different structures
to verify topology and shape.
"""

import os
import sys
import vtk
import numpy as np
import skimage
import argparse

def take_screenshot(input_filename,
                    output_filename):
    """
    Take a screenshot using 3DSlicer
    :param input_filename: str, input path to volume
                           to take screenshot of.
    :param output_filename: str, output filename to save
                            .png to.
    """
    loadedVolumeNode = slicer.util.loadVolume(input_filename)
    volRenLogic = slicer.modules.volumerendering.logic()
    displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(loadedVolumeNode)
    slicer.util.getNode("vtkMRMLGPURayCastVolumeRenderingDisplayNode1").SetVisibility(True)
    slicer.util.mainWindow().size = qt.QSize(2000,2000)
    layoutManager = slicer.app.layoutManager()
    threeDWidget = layoutManager.threeDWidget(0)
    threeDView = threeDWidget.threeDView()
    threeDView.resetFocalPoint()
    threeDView.rotateToViewAxis(3)  # look from anterior direction
    threeDView.forceRender()
    # Capture RGBA image
    renderWindow = threeDView.renderWindow()
    wti = vtk.vtkWindowToImageFilter()
    wti.SetInputBufferTypeToRGBA()
    wti.SetInput(renderWindow)
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(output_filename)
    writer.SetInputConnection(wti.GetOutputPort())
    writer.Write()
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename")
    parser.add_argument("output_filename")
    args = parser.parse_args()
    take_screenshot(args.input_filename, args.output_filename)
    