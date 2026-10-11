#version 330 core

out vec4 FragColor;

uniform vec2 uResolution;
uniform vec3 fLightingVec;
uniform mat3x3 fRotationMat;
uniform sampler2D uMapTexture;
uniform sampler2D uTemperature;

const float PI = 3.14159265358979323846;

const float MAX_HOT_TEMP_C = 30.0;
const float MIN_COLD_TEMP_C = -10.0;

const vec3 HOT_COLOR = vec3(1.0, 0.0, 0.0);
const vec3 MID_COLOR = vec3(1.0, 1.0, 1.0);
const vec3 COLD_COLOR = vec3(0.0, 0.0, 1.0);

vec3 mix3(float value, vec3 color1, vec3 color2, vec3 color3, float threshold)
{
    value = clamp(value, 0.0, 1.0);

    if (value < threshold) {
        float t = smoothstep(0.0, threshold, value);
        return mix(color1, color2, t);
    }

    float t = smoothstep(threshold, 1.0, value);
    return mix(color2, color3, t);
}

float cbrt(float x) {
    return pow(abs(x), 1.0 / 3.0) * sign(x);
}

void main()
{
    // Convert fragment coordinates to normalized coordinates.
    vec2 uv = (gl_FragCoord.xy / uResolution) * 2.0 - 1.0;

    // Correct for the aspect ratio so the sphere remains circular.
    uv.x *= uResolution.x / uResolution.y;

    // Sphere radius in this 2D coordinate system. (zoom factor using the "magnitude of the rot matrix")
    float radius = cbrt(determinant(fRotationMat));

    // Calculate squared distance from the sphere's projected center.
    float r2 = dot(uv, uv);

    // Discard fragments outside the projected sphere.
    if (r2 > radius * radius)
        discard;

    // Reconstruct the front surface of the sphere.
    float z = sqrt(radius * radius - r2);

    // Calculate the surface normal.
    vec3 normal = normalize(vec3(uv, z));


    // Simple directional lighting.
    vec3 lightDir = fRotationMat * normalize(-fLightingVec);

    float diffuse = max(dot(normal, lightDir), 0.0);

    // Calculate the map normal by rotating the surface normal
    vec3 mapNormal = normalize(transpose(fRotationMat) * normal);
    float longitude = atan(mapNormal.x, mapNormal.z);
    float latitude = asin(clamp(mapNormal.y, -1.0, 1.0));

    // Converting a point on the sphere to a point on the 2D texture.
    vec2 mapUv = vec2(
        (longitude / (2.0 * PI)) + 0.5,
        (latitude / PI) + 0.5
    );

    vec2 temperatureUv = vec2(1.0 - mapUv.x, mapUv.y);

    // The color of the map at the specific point on the sphere.
    vec3 mapColor = texture(uMapTexture, mapUv).rgb;

    float temperatureCelsius = texture(uTemperature, temperatureUv).r - 273.15;

    // Smooth normalized temperature in the range [0.0, 1.0].
    float normalizedTemperature = smoothstep(MIN_COLD_TEMP_C, MAX_HOT_TEMP_C, temperatureCelsius);

    vec3 temperatureColor = mix3(
        normalizedTemperature,
        COLD_COLOR,
        MID_COLOR,
        HOT_COLOR,
        0.5
    );

    // The surface brightness at this specific point on the sphere due to lighting.
    float brightness = clamp(0.30 + 1 * diffuse, 0.0, 1.0);

    // The final color to display on the screen.
    vec3 color = mix(mapColor, temperatureColor, 0.2) * brightness;

    FragColor = vec4(color, 1.0);
}