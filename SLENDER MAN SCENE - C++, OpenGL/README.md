# Slender Man scene (C++, OpenGL)

Final project for the Graphics Processing course (TUCN, year III): a first-person night forest scene with a skybox, shadow mapping, a flashlight spotlight, fog, a collectable page, a Dear ImGui overlay and a Slender Man model that moves between positions. The scene was assembled in Blender. Documentation and a screenshot are in `docs/`.

`main.cpp`, `Camera.*` and the shaders are mine. `Mesh`, `Model3D`, `Shader`, `SkyBox` and `Window` come from the course framework; `stb_image` and `tiny_obj_loader` are third-party.

Not included: the 3D models and textures (third-party assets), Dear ImGui, and the GLFW/GLEW/GLM libraries needed to build.
