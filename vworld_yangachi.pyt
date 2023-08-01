# -*- coding: utf-8 -*-

import arcpy
import requests
import os

from json import dumps
from pathlib import Path


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "VWorld 크롤링"
        self.alias = "VWorld 크롤링"

        # List of tool classes associated with this toolbox
        self.tools = [Ssagsre]


class Ssagsre(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "VWorld 크롤러"
        self.description = "VWorld에서 필요한 콘텐츠를 긁어온다"
        self.canRunInBackground = False
        self.X_MIN: int = 700_000
        self.X_MAX: int = 1_400_000
        self.Y_MIN: int = 1_300_000
        self.Y_MAX: int = 2_100_000
        self.X_DIFF: int = 100_000  # 기본 격자 크기
        self.Y_DIFF: int = 100_000  # 기본 격자 크기
        self.X_DELT: int = 5_000  # 보조 격자 크기 (만약 기본 격자에 1000개 이상의 피처가 있다면 한 번 더 쪼개는 용도)
        self.Y_DELT: int = 5_000  # 보조 격자 크기 (만약 기본 격자에 1000개 이상의 피처가 있다면 한 번 더 쪼개는 용도)

    def getParameterInfo(self):
        """Define parameter definitions"""
        api_key = arcpy.Parameter(
            displayName="VWorld API Key",
            name="api_key",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        layer_name = arcpy.Parameter(
            displayName="WFS Layer Name (VWorld)",
            name="layer_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        result_name = arcpy.Parameter(
            displayName="Result Feature Name",
            name="result_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        output_gdb = arcpy.Parameter(
            displayName="Output GDB",
            name="output_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        output_folder = arcpy.Parameter(
            displayName="Output Folder for JSON files",
            name="output_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
        )
        params = [api_key, layer_name, result_name, output_gdb, output_folder]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def make_api_call(self, api_key: str, layer_name: str, bbox: list) -> dict:
        """
        bbox는 xmin,ymin,xmax,ymax 형태로
        """
        resp = requests.get(
            url="http://api.vworld.kr/req/wfs",
            params={
                "request": "GetFeature",
                "key": api_key,
                "typename": layer_name,
                "output": "application/json",
                "srsname": "EPSG:5179",
                "bbox": ",".join([str(coord) for coord in bbox]),
            },
        )
        try:
            return resp.json()
        except Exception as e:
            arcpy.AddMessage(f"{e}")
            arcpy.AddMessage(f"{resp.content.decode()}")

    def execute(self, parameters, messages):
        """The source code of the tool."""
        api_key = parameters[0].valueAsText
        layer_name = parameters[1].valueAsText
        result_name = parameters[2].valueAsText
        output_gdb = Path(parameters[3].valueAsText)
        output_folder = Path(parameters[4].valueAsText)
        _json = {
            "type": "FeatureCollection",
            "totalFeatures": 0,
            "features": [],
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:EPSG::5179"},
            },
            "bbox": [
                700_000,
                1_300_000,
                1_400_000,
                2_100_000,
            ],
        }
        with open(output_folder / f"{layer_name}.json", "w", encoding="utf-8") as f:
            for x in range(self.X_MIN, self.X_MAX, self.X_DIFF):
                for y in range(self.Y_MIN, self.Y_MAX, self.Y_DIFF):
                    bbox = [x, y, x + self.X_DIFF, y + self.Y_DIFF]
                    resp = self.make_api_call(
                        api_key=api_key,
                        layer_name=layer_name,
                        bbox=bbox,
                    )

                    if resp.get("totalFeatures") > 1000:
                        for _x in range(x, x + self.X_DIFF, self.X_DELT):
                            for _y in range(y, y + self.Y_DIFF, self.Y_DELT):
                                _bbox = [_x, _y, _x + self.X_DELT, _y + self.Y_DELT]
                                _resp = self.make_api_call(
                                    api_key=api_key,
                                    layer_name=layer_name,
                                    bbox=_bbox,
                                )

                                _features = _resp.get("features") or []
                                _json["features"] += _features
                                _json["totalFeatures"] += len(_features)
                    else:
                        features = resp.get("features") or []

                        _json["features"] += features
                        _json["totalFeatures"] += len(features)
            f.write(dumps(_json))
        arcpy.conversion.JSONToFeatures(
            str(output_folder / f"{layer_name}.json"),
            str(output_gdb / result_name),
        )

        prj = arcpy.mp.ArcGISProject("CURRENT")
        _map = prj.listMaps()[0]
        _map.addDataFromPath(f"{output_gdb/result_name}")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
