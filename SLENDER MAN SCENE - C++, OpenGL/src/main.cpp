#define GLEW_STATIC
#include <GL/glew.h>
#include <GLFW/glfw3.h>

#include <glm/glm.hpp> //core glm functionality
#include <glm/gtc/matrix_transform.hpp> //glm extension for generating common transformation matrices
#include <glm/gtc/matrix_inverse.hpp> //glm extension for computing inverse matrices
#include <glm/gtc/type_ptr.hpp> //glm extension for accessing the internal data structure of glm types

#include "Window.h"
#include "Shader.hpp"
#include "Camera.hpp"
#include "Model3D.hpp"

#include <iostream>
#include "SkyBox.hpp"

#include "imgui/imgui.h"
#include "imgui/imgui_impl_glfw.h"
#include "imgui/imgui_impl_opengl3.h"

// window
gps::Window myWindow;
GLuint framebuffer;
GLuint framebufferTexture;
GLuint rectVAO, rectVBO, rbo;

// matrices
glm::mat4 model;
glm::mat4 view;
glm::mat4 projection;
glm::mat3 normalMatrix;

// light parameters
glm::vec3 lightDir;
glm::vec3 lightColor;
glm::mat4 lightRotation;
GLfloat lightAngle = 1.0f;

// shader uniform locations
GLint modelLoc;
GLint viewLoc;
GLint projectionLoc;
GLint normalMatrixLoc;
GLint lightDirLoc;
GLint lightColorLoc;
GLint onScreenTimeLoc1;
GLint onScreenTimeLoc2;
GLint framebufferTextureLoc;
bool toggleLight = false;

GLint flashPosLoc;
GLint flashDirLoc;
GLint cutOffLoc;

#define NIGHT_COLOR glm::vec3(10.0f / 255.0f, 10.0f / 255.0f, 30.0f / 255.0f);
#define WHITE_COLOR glm::vec3(1.0f, 1.0f, 1.0f);

// camera
gps::Camera myCamera(
    glm::vec3(20.0f, 0.0f, 3.0f),
    glm::vec3(-10.0f, 0.0f, 0.0f),
    glm::vec3(0.0f, 1.0f, 0.0f));

GLfloat cameraSpeed = 0.1f;
bool firstMouse = true;
float lastX = 800.0f / 2.0f;
float lastY = 600.0f / 2.0f;
float pitch = 0.0f;
float yaw = 0.0f;
float deltaTime = 0.0f;	// Time between current frame and last frame
float lastFrame = 0.0f; // Time of last frame

GLboolean pressedKeys[1024];

// models
gps::Model3D myScene;
gps::Model3D page;
gps::Model3D slender;
GLfloat angle;

// shaders
gps::Shader myCustomShader;
gps::Shader depthMapShader;
gps::Shader lightShader;
gps::Shader skyboxShader;
gps::Shader postprocessingShader;

// shadows
GLuint shadowMapFBO;
GLuint depthMapTexture;
const unsigned int SHADOW_WIDTH = 2048;
const unsigned int SHADOW_HEIGHT = 2048;

//skybox
gps::SkyBox mySkyBox;

bool isSlender = false;
bool pageCollected = false;
bool presentation = false;

float rectangleVertices[] =
{
     1.0f, -1.0f, 1.0f, 0.0f,
    -1.0f, -1.0f, 0.0f, 0.0f,
    -1.0f,  1.0f, 0.0f, 1.0f,

     1.0f,  1.0f, 1.0f, 1.0f,
     1.0f, -1.0f, 1.0f, 0.0f,
    -1.0f,  1.0f, 0.0f, 1.0f
};

GLenum glCheckError_(const char *file, int line)
{
	GLenum errorCode;
	while ((errorCode = glGetError()) != GL_NO_ERROR) {
		std::string error;
		switch (errorCode) {
            case GL_INVALID_ENUM:
                error = "INVALID_ENUM";
                break;
            case GL_INVALID_VALUE:
                error = "INVALID_VALUE";
                break;
            case GL_INVALID_OPERATION:
                error = "INVALID_OPERATION";
                break;
            case GL_STACK_OVERFLOW:
                error = "STACK_OVERFLOW";
                break;
            case GL_STACK_UNDERFLOW:
                error = "STACK_UNDERFLOW";
                break;
            case GL_OUT_OF_MEMORY:
                error = "OUT_OF_MEMORY";
                break;
            case GL_INVALID_FRAMEBUFFER_OPERATION:
                error = "INVALID_FRAMEBUFFER_OPERATION";
                break;
        }
		std::cout << error << " | " << file << " (" << line << ")" << std::endl;
	}
	return errorCode;
}
#define glCheckError() glCheckError_(__FILE__, __LINE__)

void windowResizeCallback(GLFWwindow* window, int width, int height) {
	fprintf(stdout, "Window resized! New width: %d , and height: %d\n", width, height);
	//TODO
}

void keyboardCallback(GLFWwindow* window, int key, int scancode, int action, int mode) {
	if (key == GLFW_KEY_ESCAPE && action == GLFW_PRESS) {
        glfwSetWindowShouldClose(window, GL_TRUE);
    }

	if (key >= 0 && key < 1024) {
        if (action == GLFW_PRESS) {
            pressedKeys[key] = true;
        } else if (action == GLFW_RELEASE) {
            pressedKeys[key] = false;
        }
    }
}

void mouseCallback(GLFWwindow* window, double xpos, double ypos) { 
    if (firstMouse) {
        lastX = xpos;
        lastY = ypos;
        firstMouse = false;
    }
    
    float xOffset = xpos - lastX;
    float yOffset = lastY - ypos;
    
    float sensitivity = 0.001f;
    xOffset *= sensitivity;
    yOffset *= sensitivity;
    
    yaw -= xOffset;
    pitch += yOffset;
    
    lastX = xpos;
    lastY = ypos;
    
    if (pitch > 89.0f) {
        pitch = 89.0f;
    }
    else if (pitch < -89.0f) {
        pitch = -89.0f;
    }
    
    myCamera.rotate(pitch, yaw);
    
    myCustomShader.useShaderProgram();
    view = myCamera.getViewMatrix();
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
    
    normalMatrix = glm::mat3(glm::inverseTranspose(view * model));
    glUniformMatrix3fv(normalMatrixLoc, 1, GL_FALSE, glm::value_ptr(normalMatrix));
    
    glUniform3fv(lightDirLoc, 1, glm::value_ptr(glm::inverseTranspose(glm::mat3(view)) * lightDir));
    
}

void computeDeltaTime() {
    float currentFrame = glfwGetTime();
    deltaTime = currentFrame - lastFrame;
    lastFrame = currentFrame;
}

void processMovement() {
    cameraSpeed = 4.0f * deltaTime;

	if (pressedKeys[GLFW_KEY_W]) {
		myCamera.move(gps::MOVE_FORWARD, cameraSpeed);
		//update view matrix
        view = myCamera.getViewMatrix();
        myCustomShader.useShaderProgram();
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
        // compute normal matrix for teapot
        normalMatrix = glm::mat3(glm::inverseTranspose(view*model));
	}

	if (pressedKeys[GLFW_KEY_S]) {
		myCamera.move(gps::MOVE_BACKWARD, cameraSpeed);
        //update view matrix
        view = myCamera.getViewMatrix();
        myCustomShader.useShaderProgram();
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
        // compute normal matrix for teapot
        normalMatrix = glm::mat3(glm::inverseTranspose(view*model));
	}

	if (pressedKeys[GLFW_KEY_A]) {
		myCamera.move(gps::MOVE_LEFT, cameraSpeed);
        //update view matrix
        view = myCamera.getViewMatrix();
        myCustomShader.useShaderProgram();
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
        // compute normal matrix for teapot
        normalMatrix = glm::mat3(glm::inverseTranspose(view*model));
	}

	if (pressedKeys[GLFW_KEY_D]) {
		myCamera.move(gps::MOVE_RIGHT, cameraSpeed);
        //update view matrix
        view = myCamera.getViewMatrix();
        myCustomShader.useShaderProgram();
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
        // compute normal matrix for teapot
        normalMatrix = glm::mat3(glm::inverseTranspose(view*model));
	}

    if (pressedKeys[GLFW_KEY_J]) {
        lightAngle -= 1.0f;
        model = glm::rotate(glm::mat4(1.0f), glm::radians(angle), glm::vec3(0, 1, 0));
        // update normal matrix for teapot
        normalMatrix = glm::mat3(glm::inverseTranspose(view * model));
    }

    if (pressedKeys[GLFW_KEY_L]) {
        lightAngle += 1.0f;
        model = glm::rotate(glm::mat4(1.0f), glm::radians(angle), glm::vec3(0, 1, 0));
        // update normal matrix for teapot
        normalMatrix = glm::mat3(glm::inverseTranspose(view * model));
    }
    if (pressedKeys[GLFW_KEY_F]) {
        toggleLight = !toggleLight;
    }
    if (pressedKeys[GLFW_KEY_Z]) {
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
    }

    if (pressedKeys[GLFW_KEY_X]) {
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
    }
    if (pressedKeys[GLFW_KEY_C]) {
        glPolygonMode(GL_FRONT_AND_BACK, GL_POINT);
    }
    if (pressedKeys[GLFW_KEY_Q]) {
        presentation = !presentation;
    }

}

void initOpenGLWindow() {
    myWindow.Create(1920, 1080, "My scene");
}

void setWindowCallbacks() {
	glfwSetWindowSizeCallback(myWindow.getWindow(), windowResizeCallback);
    glfwSetKeyCallback(myWindow.getWindow(), keyboardCallback);
    glfwSetCursorPosCallback(myWindow.getWindow(), mouseCallback);
}

void initOpenGLState() {
    glClearColor(0.5, 0.5, 0.5, 1.0);
	//glClearColor(0.7f, 0.7f, 0.7f, 1.0f);
	glViewport(0, 0, myWindow.getWindowDimensions().width, myWindow.getWindowDimensions().height);
    glEnable(GL_FRAMEBUFFER_SRGB);
	glEnable(GL_DEPTH_TEST); // enable depth-testing
	glDepthFunc(GL_LESS); // depth-testing interprets a smaller value as "closer"
	glEnable(GL_CULL_FACE); // cull face
	glCullFace(GL_BACK); // cull back face
	glFrontFace(GL_CCW); // GL_CCW for counter clock-wise
    glfwSetInputMode(myWindow.getWindow(), GLFW_CURSOR, GLFW_CURSOR_DISABLED); // hide cursor
}

void initImgui() {
    // Setup Dear ImGui context
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO(); (void)io;
    ImGui::CreateContext();
    //io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;     // Enable Keyboard Controls
    //io.ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad;      // Enable Gamepad Controls

    // Setup Dear ImGui style
    ImGui::StyleColorsDark();

    // Setup Platform/Renderer backends
    ImGui_ImplGlfw_InitForOpenGL(myWindow.getWindow(), true);
    ImGui_ImplOpenGL3_Init("#version 130");
}

void initShaders() {
    myCustomShader.loadShader(
        "shaders/shaderStart.vert",
        "shaders/shaderStart.frag");
    myCustomShader.useShaderProgram();

    depthMapShader.loadShader(
        "shaders/depthMapShader.vert",
        "shaders/depthMapShader.frag");
    depthMapShader.useShaderProgram();

    skyboxShader.loadShader(
        "shaders/skyboxShader.vert",
        "shaders/skyboxShader.frag");
}

void initUniforms() {
    myCustomShader.useShaderProgram();

    // create model matrix for teapot
    model = glm::rotate(glm::mat4(1.0f), glm::radians(angle), glm::vec3(0.0f, 1.0f, 0.0f));
    modelLoc = glGetUniformLocation(myCustomShader.shaderProgram, "model");

    // get view matrix for current camera
    view = myCamera.getViewMatrix();
    viewLoc = glGetUniformLocation(myCustomShader.shaderProgram, "view");
    // send view matrix to shader
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));

    // compute normal matrix for teapot
    normalMatrix = glm::mat3(glm::inverseTranspose(view * model));
    normalMatrixLoc = glGetUniformLocation(myCustomShader.shaderProgram, "normalMatrix");

    // create projection matrix
    projection = glm::perspective(glm::radians(45.0f),
        (float)myWindow.getWindowDimensions().width / (float)myWindow.getWindowDimensions().height,
        0.1f, 100.0f);
    projectionLoc = glGetUniformLocation(myCustomShader.shaderProgram, "projection");
    // send projection matrix to shader
    glUniformMatrix4fv(projectionLoc, 1, GL_FALSE, glm::value_ptr(projection));

    //set the light direction (direction towards the light)
    lightDir = glm::vec3(0.0f, 1.0f, 1.0f);
    lightDirLoc = glGetUniformLocation(myCustomShader.shaderProgram, "lightDir");
    // send light dir to shader
    glUniform3fv(lightDirLoc, 1, glm::value_ptr(lightDir));

    //set light color
    lightColor = NIGHT_COLOR;
    lightColorLoc = glGetUniformLocation(myCustomShader.shaderProgram, "lightColor");
    // send light color to shader
    glUniform3fv(lightColorLoc, 1, glm::value_ptr(lightColor));

    //flashlight uniform positions
    flashPosLoc = glGetUniformLocation(myCustomShader.shaderProgram, "flashPos");
    flashDirLoc = glGetUniformLocation(myCustomShader.shaderProgram, "flashDir");

    //Slender Man's time on screen
    onScreenTimeLoc1 = glGetUniformLocation(myCustomShader.shaderProgram, "onScreenTime");
    skyboxShader.useShaderProgram();
    onScreenTimeLoc2 = glGetUniformLocation(skyboxShader.shaderProgram, "onScreenTime");

    //screen texture
    //postprocessingShader.useShaderProgram();
    //framebufferTextureLoc = glGetUniformLocation(postprocessingShader.shaderProgram, "framebufferTexture");
    //glUniform1i(framebufferTextureLoc, 0);
}

void initFBO() {

    glGenFramebuffers(1, &shadowMapFBO);

    //create depth texture for FBO
    glGenTextures(1, &depthMapTexture);
    glBindTexture(GL_TEXTURE_2D, depthMapTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT,
        SHADOW_WIDTH, SHADOW_HEIGHT, 0, GL_DEPTH_COMPONENT, GL_FLOAT, NULL);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    float borderColor[] = { 1.0f, 1.0f, 1.0f, 1.0f };
    glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);

    //attach texture to FBO
    glBindFramebuffer(GL_FRAMEBUFFER, shadowMapFBO);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depthMapTexture, 0);

    //initialize FBO
    glDrawBuffer(GL_NONE);
    glReadBuffer(GL_NONE);

    glBindFramebuffer(GL_FRAMEBUFFER, 0);

    //vao and vbo
    //glGenVertexArrays(1, &rectVAO);
    //glGenBuffers(1, &rectVBO);
    //glBindVertexArray(rectVAO);
    //glBindBuffer(GL_ARRAY_BUFFER, rectVBO);
    //glBufferData(GL_ARRAY_BUFFER, sizeof(rectangleVertices), &rectangleVertices, GL_STATIC_DRAW);
    //glEnableVertexAttribArray(0);
    //glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)0);
    //glEnableVertexAttribArray(1);
    //glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)(2 * sizeof(float)));
    
    //FBO for Slender Man effect
    //glGenFramebuffers(2, &framebuffer);
    //glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    //
    ////generate texture
    //glGenTextures(2, &framebufferTexture);
    //glBindTexture(GL_TEXTURE_2D, framebufferTexture);
    //glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1920, 1080, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);
    //glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    //glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    //glBindTexture(GL_TEXTURE_2D, 0);
    //
    ////attach it to currently bound framebuffer object
    //glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, framebufferTexture, 0);
    //
    ////render buffer because yea
    //glGenRenderbuffers(1, &rbo);
    //glBindRenderbuffer(GL_RENDERBUFFER, rbo);
    //glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 1920, 1080);
    //glBindRenderbuffer(GL_RENDERBUFFER, 0);
    //
    //glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo);
    //
    //if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
    //    std::cout << "ERROR::FRAMEBUFFER:: Framebuffer is not complete!" << std::endl;
    //glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void initModels() {
    //init models
    myScene.LoadModel("models/MYSCENE/MYSCENE2.obj", "models/MYSCENE/");
    slender.LoadModel("models/MYSCENE/Slenderman.obj", "models/MYSCENE/");
    page.LoadModel("models/MYSCENE/Page.obj", "models/MYSCENE/");

    //init skybox
    std::vector<const GLchar*> faces;
    faces.push_back("models/nightsky/nightsky_rt.tga");
    faces.push_back("models/nightsky/nightsky_lf.tga");
    faces.push_back("models/nightsky/nightsky_up.tga");
    faces.push_back("models/nightsky/nightsky_dn.tga");
    faces.push_back("models/nightsky/nightsky_bk.tga");
    faces.push_back("models/nightsky/nightsky_ft.tga");
    mySkyBox.Load(faces);
}

float onScreenTime = 1.0f;
float rotation = 1.0f;
float angleCam = 1.0f;
int sec = 0;
int pos = 0;
int slenderTime = 0;
glm::mat4 modell = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, -5.0f, 0.0f));
void drawObjects(gps::Shader shader, bool depthPass) {
    //select active shader program
    shader.useShaderProgram();
    if (presentation) {
        lightRotation = glm::rotate(glm::mat4(1.0f), glm::radians(rotation), glm::vec3(0.0f, 1.0f, 0.0f));
        model = lightRotation;
        model = glm::translate(model, 1.0f * lightDir);
        model = glm::translate(model, glm::vec3(0.0f, -3.0f, 10.0f));
        model = glm::scale(model, glm::vec3(0.20f));
        onScreenTime = 1.0f;

        //model = glm::mat4(1.0f);
        //
        //model = glm::rotate(model, glm::radians(angleCam), glm::vec3(0.0f, 1.0f, 0.0f));
        //model = glm::translate(model, glm::vec3(6.9f, 6.56f, 10.9f));
        //glm::vec3 pos = glm::vec3((model * glm::vec4(1.0f)));
        //myCamera.cameraPosition = pos;
        //myCamera.cameraTarget = glm::vec3(0.0f, 0.0f, 0.0f);
    }
    else {
        model = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, -5.0f, 0.0f));
    }

    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    if (!depthPass) {
        normalMatrix = glm::mat3(glm::inverseTranspose(view * model));
        glUniformMatrix3fv(normalMatrixLoc, 1, GL_FALSE, glm::value_ptr(normalMatrix));
    }
    myScene.Draw(shader);
    if (!pageCollected) {
        page.Draw(shader);
    }

    if (sec == 300 && !presentation) {
        if (pos % 3 == 0) {
            modell = glm::translate(glm::mat4(1.0f), glm::vec3(12.2f, -5.0f, -15.9f));
        }
        if (pos % 3 == 1) {
            modell = glm::translate(glm::mat4(1.0f), glm::vec3(-9.8f, -5.0f, -14.6f));
        }
        if (pos % 3 == 2) {
            modell = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, -5.0f, 0.0f));
        }
        sec = 0;
        pos++;
    }
    sec++;
    model = modell;
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));

    slender.Draw(shader);
}

glm::mat4 computeLightSpaceTrMatrix() {
    const GLfloat near_plane = 0.1f, far_plane = 25.0f;

    glm::mat4 lightView = glm::lookAt(glm::mat3(lightRotation) * 5.0f * lightDir, glm::vec3(0.0f), glm::vec3(0.0f, 1.0f, 0.0f));
    glm::mat4 lightProjection = glm::ortho(-15.0f, 15.0f, -15.0f, 15.0f, near_plane, far_plane);
    glm::mat4 lightSpaceTrMatrix = lightProjection * lightView;
    return lightSpaceTrMatrix;
}


void checkSlender() {
    float x = myCamera.cameraPosition.x;
    float y = myCamera.cameraPosition.y;
    float z = myCamera.cameraPosition.z;

    if ((x < 9.6f && z > 15.0f || x < 2.4f) && y < 4.0f) {
        isSlender = true;
        if (onScreenTime < 5.5f) {
            onScreenTime += 0.05f;
        }
    }
    else {
        isSlender = false;
        if (onScreenTime > 1.0f) {
            onScreenTime -= 0.07f;
        }
    }

    myCustomShader.useShaderProgram();
    glUniform1f(onScreenTimeLoc1, onScreenTime);
    skyboxShader.useShaderProgram();
    glUniform1f(onScreenTimeLoc2, onScreenTime);

    if (x < 12.5f && -1.2f < z && z < -0.2f) {
        pageCollected = true;
    }
}

void renderImgui() {
    glfwPollEvents();
    ImGui::SetWindowSize(ImVec2(350, 100));  
    ImGui::Text("X: %.01f, Y: %.01f, Z: %.01f", myCamera.cameraPosition.x, myCamera.cameraPosition.y, myCamera.cameraPosition.z);
    ImGui::Text("SlenderMan: %s", isSlender ? "True" : "False");
    ImGui::Text("Application average %.3f ms/frame (%.1f FPS)", 1000.0f / ImGui::GetIO().Framerate, ImGui::GetIO().Framerate);
    ImGui::End();
}


void renderScene() {
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    //ImGui frame
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();

    //checks for SlenderMan
    checkSlender();
    

    //render the scene in the depth map
    depthMapShader.useShaderProgram();
    glUniformMatrix4fv(glGetUniformLocation(depthMapShader.shaderProgram, "lightSpaceTrMatrix"),
        1,
        GL_FALSE,
        glm::value_ptr(computeLightSpaceTrMatrix()));


    glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT);
    glBindFramebuffer(GL_FRAMEBUFFER, shadowMapFBO);
    glClear(GL_DEPTH_BUFFER_BIT);

    drawObjects(depthMapShader, true);

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    //final scene rendering pass (with shadows)
    glViewport(0, 0, myWindow.getWindowDimensions().width, myWindow.getWindowDimensions().height);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    myCustomShader.useShaderProgram();
    glUniform1f(glGetUniformLocation(myCustomShader.shaderProgram, "time"), slenderTime);
    slenderTime++;
    //light roatation
    view = myCamera.getViewMatrix();
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
    lightRotation = glm::rotate(glm::mat4(1.0f), glm::radians(lightAngle), glm::vec3(0.0f, 1.0f, 0.0f));
    glUniform3fv(lightDirLoc, 1, glm::value_ptr(glm::inverseTranspose(glm::mat3(view * lightRotation)) * lightDir));

    if (!toggleLight) {
        lightColor = NIGHT_COLOR;
        lightColorLoc = glGetUniformLocation(myCustomShader.shaderProgram, "lightColor");
        // send light color to shader
        glUniform3fv(lightColorLoc, 1, glm::value_ptr(lightColor));
    }
    else {
        lightColor = WHITE_COLOR;
        lightColorLoc = glGetUniformLocation(myCustomShader.shaderProgram, "lightColor");
        // send light color to shader
        glUniform3fv(lightColorLoc, 1, glm::value_ptr(lightColor));
    }

    rotation += 0.5f;
    angleCam -= 0.1f;

    //bind the shadow map
    glActiveTexture(GL_TEXTURE3);
    glBindTexture(GL_TEXTURE_2D, depthMapTexture);
    glUniform1i(glGetUniformLocation(myCustomShader.shaderProgram, "shadowMap"), 3);
    glUniformMatrix4fv(glGetUniformLocation(myCustomShader.shaderProgram, "lightSpaceTrMatrix"),1 , GL_FALSE, glm::value_ptr(computeLightSpaceTrMatrix()));

    //draw objects with shadows
	drawObjects(myCustomShader, false);

    //flashlight
    glUniform3fv(flashPosLoc, 1, glm::value_ptr(myCamera.cameraPosition));
    glUniform3fv(flashDirLoc, 1, glm::value_ptr(myCamera.cameraFrontDirection));

    //draw skybox
    skyboxShader.useShaderProgram();
    view = myCamera.getViewMatrix();
    glUniformMatrix4fv(glGetUniformLocation(skyboxShader.shaderProgram, "view"), 1, GL_FALSE, glm::value_ptr(view));
    projection = glm::perspective(glm::radians(45.0f), 1920.0f / 1080.0f, 0.1f, 1000.0f);
    glUniformMatrix4fv(glGetUniformLocation(skyboxShader.shaderProgram, "projection"), 1, GL_FALSE, glm::value_ptr(projection));
    mySkyBox.Draw(skyboxShader, view, projection);

    //glBindFramebuffer(GL_FRAMEBUFFER, 0); // back to default
    //glClear(GL_COLOR_BUFFER_BIT);
    //myCustomShader.useShaderProgram();
    //glBindVertexArray(rectVAO);
    //glDisable(GL_DEPTH_TEST);
    //glBindTexture(GL_TEXTURE_2D, framebufferTexture);
    //glDrawArrays(GL_TRIANGLES, 0, 6);

    renderImgui();

    ImGui::Render();
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
}

void cleanup() {
    myWindow.Delete();
    //cleanup code for your own data
}

int main(int argc, const char * argv[]) {

    try {
        initOpenGLWindow();
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return EXIT_FAILURE;
    }

    initOpenGLState();
    initImgui();
	initModels();
	initShaders();
    initFBO();
	initUniforms();
    setWindowCallbacks();

	glCheckError();
	// application loop
	while (!glfwWindowShouldClose(myWindow.getWindow())) {
        computeDeltaTime();
        processMovement();
	    renderScene();
        glCheckError();

		glfwPollEvents();
        glCheckError();
		glfwSwapBuffers(myWindow.getWindow());

		glCheckError();
	}

    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
	cleanup();

    return EXIT_SUCCESS;
}
