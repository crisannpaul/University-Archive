//
//  projection.cpp
//  Lab8_TODO
//
//  Copyright © 2016 CGIS. All rights reserved.
//
#include "include/SDL.h"
#include "projection.h"

namespace egc {
    //define the viewport transformation matrix
    //see section 3 from the laboratory work
    mat4 defineViewTransformMatrix(int startX, int startY, int width, int height)
    {
		mat4 viewTransformMatrix;
        viewTransformMatrix.at(0, 0) = (float) (width / 2.0);
        viewTransformMatrix.at(1, 1) = (float) (height / 2.0) * -1;
        viewTransformMatrix.at(0, 3) = (float) (width / 2.0 + startX);
        viewTransformMatrix.at(1, 3) = (float) (height / 2.0 + startY);

        return viewTransformMatrix;
    }
    
    //define the camera transformation matrix
    //see section 4 from the laboratory work
    mat4 defineCameraMatrix(Camera mc)
    {
        mat4 cameraMatrix, m1, m2;
        vec3 w = (mc.cameraTarget - mc.cameraPosition).normalize() * -1;
        vec3 u = crossProduct(mc.cameraUp, w).normalize();
        vec3 v = crossProduct(w, u);

        m1.at(0, 0) = u.x;    m1.at(0, 1) = u.y;    m1.at(0, 2) = u.z;
        m1.at(1, 0) = v.x;    m1.at(1, 1) = v.y;    m1.at(1, 2) = v.z;
        m1.at(2, 0) = w.x;    m1.at(2, 1) = w.y;    m1.at(2, 2) = w.z;
       
        m2.at(0, 3) = -1 * mc.cameraPosition.x;
        m2.at(1, 3) = -1 * mc.cameraPosition.y;
        m2.at(2, 3) = -1 * mc.cameraPosition.z;

        cameraMatrix = m1 * m2;

        return cameraMatrix;
    }
    
    //define the projection transformation matrix
    //see section 5 from the laboratory work
    mat4 definePerspectiveProjectionMatrix(float fov, float aspect, float zNear, float zFar)
    {
        mat4 perspectiveProjectionMatrix;
        auto tang = tan(fov / 2.0);

        perspectiveProjectionMatrix.at(0, 0) = (float) (-1.0 / (aspect * tang));
        perspectiveProjectionMatrix.at(1, 1) = (float) (-1.0 / tang);
        perspectiveProjectionMatrix.at(2, 2) = (zFar + zNear) / (zNear - zFar);
        perspectiveProjectionMatrix.at(2, 3) = (float) ((2.0 * zFar * zNear) / (zFar - zNear));
        perspectiveProjectionMatrix.at(3, 2) = 1.0;
        perspectiveProjectionMatrix.at(3, 3) = 0.0;

        return perspectiveProjectionMatrix;
    }
    
    //define the perspective divide operation
    //see section 5 from the laboratory work
    void perspectiveDivide(vec4 &iv)
    {
        iv = iv * (1.0f / iv.w);
    }

    //check if a point should be clipped
    //see section 9 from the laboratory work
    bool clipPointInHomogeneousCoordinate(const egc::vec4 &vertex)
    {
        return !(((-1 * abs(vertex.w)) <= vertex.x && vertex.x <= abs(vertex.w)) &&
            ((-1 * abs(vertex.w)) <= vertex.y && vertex.y <= abs(vertex.w)) &&
            ((-1 * abs(vertex.w)) <= vertex.z && vertex.z <= abs(vertex.w)));
    }

    //check if a triangle should be clipped
    //clip only those triangles for which all vertices are outside the viewing volume
    bool clipTriangleInHomegeneousCoordinates(const std::vector<egc::vec4> &triangle)
    {
        return clipPointInHomogeneousCoordinate(triangle.at(0)) && clipPointInHomogeneousCoordinate(triangle.at(1)) &&
              clipPointInHomogeneousCoordinate(triangle.at(2));
    }

    //compute the normal vector to a triangle
    //see section 7 from the laboratory work
    egc::vec3 findNormalVectorToTriangle(const std::vector<egc::vec4> &triangle)
    {
        egc::vec3 n;

        n = crossProduct((triangle.at(0) - triangle.at(1)), (triangle.at(2) - triangle.at(1))).normalize();
        
        return n;
    }

    //compute the coordinates of the triangle's center
    //(we will use this point to display the normal vector)
    egc::vec4 findCenterPointOfTriangle(const std::vector<egc::vec4> &triangle)
    {
        egc::vec4 triangleCenter;
        triangleCenter.x = (triangle.at(0).x + triangle.at(1).x + triangle.at(2).x)/3.0f;
        triangleCenter.y = (triangle.at(0).y + triangle.at(1).y + triangle.at(2).y)/3.0f;
        triangleCenter.z = (triangle.at(0).z + triangle.at(1).z + triangle.at(2).z)/3.0f;
        triangleCenter.w = (triangle.at(0).w + triangle.at(1).w + triangle.at(2).w)/3.0f;
        
        return triangleCenter;
    }

    //check if the triangle is visible (front facing)
    //see section 8 from the laboratory work
    bool isTriangleVisible(const std::vector<egc::vec4> &triangle, const egc::vec3 &normalVector)
    {
        return dotProduct(triangle.at(0), normalVector) > 0 ||
            dotProduct(triangle.at(1), normalVector) > 0 ||
            dotProduct(triangle.at(2), normalVector) > 0;
    }

    void displayNormalVectors(egc::vec3& normalVector, egc::vec4& triangleCenter)
    {
    }

    //display the normal vector of a triangle
    //see section 7 from the laboratory work
    //use the SDL_RenderDrawLine to draw the normal vector
    void displayNormalVectors(egc::vec3& normalVector, egc::vec4& triangleCenter, SDL_Renderer* renderer, egc::mat4 viewTransformMatrix, egc::mat4 perspectiveMatrix)
    {
        egc::vec4 centerPoint = triangleCenter;
        centerPoint = perspectiveMatrix * centerPoint;
        perspectiveDivide(centerPoint);
        centerPoint = viewTransformMatrix * centerPoint;
        egc::vec4 secondPoint;

        secondPoint.x = centerPoint.x + (normalVector.x * 15.0f);
        secondPoint.y = centerPoint.y + (normalVector.y * 15.0f);
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, 0);
        SDL_RenderDrawLine(renderer, (int) centerPoint.x, (int)centerPoint.y, (int)secondPoint.x, (int)secondPoint.y);
    }
}
