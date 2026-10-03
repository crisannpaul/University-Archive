#include "Camera.hpp"
#include <glm/gtx/euler_angles.hpp>

namespace gps {

    //Camera constructor
    Camera::Camera(glm::vec3 cameraPosition, glm::vec3 cameraTarget, glm::vec3 cameraUp) {
        this->cameraPosition = cameraPosition;
        this->cameraTarget = cameraTarget;
        this->cameraUpDirection = cameraUp;
        this->cameraOriginalUp = cameraUp;
        Camera::cameraRightDirection = glm::vec3(1.0f, 0.0f, 0.0f);
        Camera::cameraFrontDirection = glm::vec3(0.0f, 0.0f, -1.0f);
        //TODO - Update the rest of camera parameters
    }

    //return the view matrix, using the glm::lookAt() function
    glm::mat4 Camera::getViewMatrix() {
        return glm::lookAt(cameraPosition, cameraTarget, cameraUpDirection);
    }

    //update the camera internal parameters following a camera move event
    void Camera::move(MOVE_DIRECTION direction, float speed) {
        if (direction == MOVE_FORWARD) {
            cameraPosition += speed * cameraFrontDirection;
        }
        if (direction == MOVE_BACKWARD) {
            cameraPosition -= speed * cameraFrontDirection;
        }
        if (direction == MOVE_RIGHT) {
            cameraPosition += speed * cameraRightDirection;
        }
        if (direction == MOVE_LEFT) {
            cameraPosition -= speed * cameraRightDirection;
        }
        cameraTarget = cameraPosition + cameraFrontDirection;
    }

    //update the camera internal parameters following a camera rotate event
    //yaw - camera rotation around the y axis
    //pitch - camera rotation around the x axis
    void Camera::rotate(float pitch, float yaw) {
        glm::mat4 rotationMatrix = glm::yawPitchRoll(yaw, pitch, 0.0f);
        glm::vec4 frontVector = rotationMatrix * glm::vec4(0.0f, 0.0f, -1.0f, 0.0f);
        
        this->cameraFrontDirection = glm::normalize(frontVector);
        this->cameraRightDirection = glm::normalize(glm::cross(cameraFrontDirection, cameraOriginalUp));
        this->cameraUpDirection = glm::normalize(glm::cross(cameraRightDirection, cameraFrontDirection));
        
        this->cameraTarget = this->cameraPosition + this->cameraFrontDirection;
    }
}