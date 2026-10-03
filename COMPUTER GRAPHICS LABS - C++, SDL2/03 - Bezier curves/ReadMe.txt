#include "Bezier.h"
#include "math.h"
#include <vector>

//Return the value of P(t), where t is in [0,1]
vec2 getParametricPoint(float t, vec2 p0, vec2 p1) {
	//P(t) = (1 - t)*P0 + t*P1
	vec2 point;
	point = p0*(1 - t) + p1*t;
	return point;
}

//Paint the pixels that are on the line P0P1
void drawParametricLinePoints(vec2 p0, vec2 p1, SDL_Renderer* renderer) {
	//Hint: To paint a single pixel, you can use the function: SDL_RenderDrawPoint(renderer, x, y)
	for (float i = 0; i <= 1; i+=0.0005)
	{
		vec2 tmp = getParametricPoint(i, p0, p1);
		SDL_RenderDrawPoint(renderer, tmp.x, tmp.y);
	}
}

//Return the value of B(t), where t is in [0,1]. The value of B(t) is computed by taking into account all the 
//controll points contained within the input vecto
vec2 getBezierPoint(std::vector<vec2> controlPoints, float t) {
	vec2 point;

	if (controlPoints.size() == 2)
	{
		point = controlPoints[0] * (1 - t) + controlPoints[1] * t;
		return point;
	}

	std::vector<vec2> pn_1;
	std::vector<vec2> pn;
	for (int i = 0; i < controlPoints.size() - 1; i++)
		pn_1.push_back(controlPoints[i]);
	for (int i = 1; i < controlPoints.size(); i++)
		pn.push_back(controlPoints[i]);

	point = getBezierPoint(pn_1, t) * (1 - t) + getBezierPoint(pn, t) * t;

	return point;
}

//Paint the pixels that are on the Bezier curve defined by the given control points
void drawBezierPoints(std::vector<vec2> controlPoints, SDL_Renderer* renderer) {
	for (float i = 0; i <= 1; i += 0.0005)
	{
		vec2 temp = getBezierPoint(controlPoints, i);
		SDL_RenderDrawPoint(renderer, temp.x, temp.y);
	}
}

========================================================================
    CONSOLE APPLICATION : EGC_Bezier Project Overview
========================================================================

AppWizard has created this EGC_Bezier application for you.

This file contains a summary of what you will find in each of the files that
make up your EGC_Bezier application.


EGC_Bezier.vcxproj
    This is the main project file for VC++ projects generated using an Application Wizard.
    It contains information about the version of Visual C++ that generated the file, and
    information about the platforms, configurations, and project features selected with the
    Application Wizard.

EGC_Bezier.vcxproj.filters
    This is the filters file for VC++ projects generated using an Application Wizard. 
    It contains information about the association between the files in your project 
    and the filters. This association is used in the IDE to show grouping of files with
    similar extensions under a specific node (for e.g. ".cpp" files are associated with the
    "Source Files" filter).

EGC_Bezier.cpp
    This is the main application source file.

/////////////////////////////////////////////////////////////////////////////
Other standard files:

StdAfx.h, StdAfx.cpp
    These files are used to build a precompiled header (PCH) file
    named EGC_Bezier.pch and a precompiled types file named StdAfx.obj.

/////////////////////////////////////////////////////////////////////////////
Other notes:

AppWizard uses "TODO:" comments to indicate parts of the source code you
should add to or customize.

/////////////////////////////////////////////////////////////////////////////
