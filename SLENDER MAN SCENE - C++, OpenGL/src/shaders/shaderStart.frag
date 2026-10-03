#version 410 core

in vec3 fNormal;
in vec4 fPosEye;
in vec2 fTexCoords;
in vec4 fragPosLightSpace;
in vec4 fragPosWorld;

out vec4 fColor;

//lighting
uniform	vec3 lightDir;
uniform	vec3 lightColor;

//flashight
uniform vec3 flashPos;
uniform vec3 flashDir;
uniform float cutOff;

//texture
uniform sampler2D diffuseTexture;
uniform sampler2D specularTexture;
uniform sampler2D shadowMap;
uniform sampler2D framebufferTexture;
uniform float onScreenTime;
uniform float time;

vec3 ambient;
float ambientStrength = 0.2f;
vec3 diffuse;
vec3 specular;
float specularStrength = 0.5f;
float shininess = 32.0f;

void computeLightComponents()
{		
	vec3 cameraPosEye = vec3(0.0f);//in eye coordinates, the viewer is situated at the origin
	
	//transform normal
	vec3 normalEye = normalize(fNormal);	
	
	//compute light direction
	vec3 lightDirN = normalize(lightDir);
	
	//compute view direction 
	vec3 viewDirN = normalize(cameraPosEye - fPosEye.xyz);
		
	//compute ambient light
	ambient = ambientStrength * lightColor;
	
	//compute diffuse light
	diffuse = max(dot(normalEye, lightDirN), 0.0f) * lightColor;
	
	//compute specular light
	vec3 reflection = reflect(-lightDirN, normalEye);
	float specCoeff = pow(max(dot(viewDirN, reflection), 0.0f), shininess);
	specular = specularStrength * specCoeff * lightColor;
}

float computeShadow()
{
	//perspective divide and transform to [0,1] range
	vec3 normalizedCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
	normalizedCoords = normalizedCoords * 0.5 + 0.5;

	if (normalizedCoords.z > 1.0f)
		return 0.0f;

	//get closest/current depth value from light's perspective
	float closestDepth = texture(shadowMap, normalizedCoords.xy).r;
	float currentDepth = normalizedCoords.z;

	float bias = max(0.05f * (1.0f - dot(fNormal, lightDir)), 0.005f);
	float shadow = currentDepth - bias > closestDepth ? 1.0f : 0.0f;
	return shadow;
}

float computeFog()
{
 float fogDensity = 0.015f * onScreenTime;
 float fragmentDistance = length(fPosEye);
 float fogFactor = exp(-pow(fragmentDistance * fogDensity, 2));

 return clamp(fogFactor, 0.0f, 1.0f);
}

vec3 computeFlashlight(vec3 flashPos) {
	float flashLinear = 0.1f;
	float flashQuadratic = 0.03f;
	vec3 lightFlashColor = vec3(1.0f);

	float shininessFlash = 100.0f;
	float constant=0.0f;
	
	float cutOff = cos(radians(5.5f));
	float outerCutOff = cos(radians(15.0f));
	
	vec3 viewDir = normalize(flashPos - fragPosWorld.xyz);
    vec3 lightDirFlashLocal = normalize(flashPos - fragPosWorld.xyz);
	
    // Diffuse shading
    float diff = max(dot(fNormal, lightDirFlashLocal), 0.0);
	
    // Specular shading
    vec3 reflectDir = reflect(-lightDirFlashLocal, fNormal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininessFlash);
	
    // Attenuation
    float distance = length(flashPos - fragPosWorld);
    float attenuation = 1.0f / (constant + flashLinear * distance + flashQuadratic * (distance * distance));    
   
    // Spotlight intensity
    float theta = dot(lightDirFlashLocal, normalize(-flashDir)); 
    float epsilon = cutOff - outerCutOff;
    float intensity = clamp((theta - outerCutOff) / epsilon, 0.0, 1.0);
    
	// Combine results
    vec3 ambientFlash = vec3(texture(diffuseTexture, fTexCoords)) * lightFlashColor;
    vec3 diffuseFlash = diff * vec3(texture(diffuseTexture, fTexCoords)) * lightFlashColor;
    vec3 specularFlash = spec * vec3(texture(specularTexture, fTexCoords)) * lightFlashColor;
    ambientFlash *= attenuation * intensity;
    diffuseFlash *= attenuation * intensity;
    specularFlash *= attenuation * intensity;

    return (ambientFlash + diffuseFlash + specularFlash);
}

const float e = 2.7182818284590452353602874713527;
vec4 noise(vec2 texCoord)
{
    float G = e + (time * 0.1);
    vec2 r = (G * sin(G * texCoord.xy));
    return vec4(fract(r.x * r.y * (1.0 + texCoord.x)));
}

void main() 
{
	computeLightComponents();
	
	ambient *= texture(diffuseTexture, fTexCoords).rgb;
	diffuse *= texture(diffuseTexture, fTexCoords).rgb;
	specular *= texture(specularTexture, fTexCoords).rgb;

	float shadow = computeShadow();

	vec3 color = min((ambient + (1.0f - shadow) * diffuse) + (1.0f - shadow) * specular, 1.0f);

	vec3 flashlightColor = computeFlashlight(flashPos);
	vec3 finalColor = min(color + flashlightColor, 1.0f);
    
	float fogFactor = computeFog();
	vec3 fogColor = vec3(0.7f, 0.7f, 0.7f);

	vec4 noise = vec4(1.0f);
	if(onScreenTime > 1.0f) {
		noise = noise(fTexCoords);
	}
	//fColor = texture(framebufferTexture, fTexCoords);
	fColor = vec4(mix(fogColor, finalColor, fogFactor), 1.0f);
	fColor *= noise;
}
