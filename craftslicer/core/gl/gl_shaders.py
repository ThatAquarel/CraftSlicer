vertex_shader = """
# version 330
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec4 a_color;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec4 v_color;
void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);
    v_color = a_color;
}
"""

fragment_shader = """
# version 330
in vec4 v_color;

out vec4 out_color;
void main()
{
    out_color = v_color;
}
"""
