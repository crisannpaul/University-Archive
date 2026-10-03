#version 410 core

in vec3 textureCoordinates;
out vec4 fColor;

uniform float onScreenTime;

uniform samplerCube skybox;

float computeFog()
{
 float fogDensity = 0.015f * onScreenTime;
 float fragmentDistance = 50.1f;
 float fogFactor = exp(-pow(fragmentDistance * fogDensity, 2));

 return clamp(fogFactor, 0.0f, 1.0f);
}
void main()
{
    float fogFactor = computeFog();
	vec3 fogColor = vec3(0.7f, 0.7f, 0.7f);

    vec4 color = texture(skybox, textureCoordinates);
    fColor = fogColor * (1 - fogFactor) + color * fogFactor;
}
