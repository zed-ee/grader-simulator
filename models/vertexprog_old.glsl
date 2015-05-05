//GLSL
uniform sampler2D ground;
uniform sampler2D snow
uniform sampler2D tracks;
uniform vec4 snowHeight;

#define textureSize 257.0
#define texelSize 1.0 / 257.0

#define plane_size 250.0

vec4 tex2D_bilinear(sampler2D tex, vec2 t )
{
    vec2 f = fract( t.xy * textureSize );
    vec4 t00 = texture2D( tex, t );
    vec4 t10 = texture2D( tex, t + vec2( texelSize, 0.0 ));
    vec4 tA = mix( t00, t10, f.x );
    vec4 t01 = texture2D( tex, t + vec2( 0.0, texelSize ) );
    vec4 t11 = texture2D( tex, t + vec2( texelSize, texelSize ) );
    vec4 tB = mix( t01, t11, f.x );
    return mix( tA, tB, f.y );
}	
	
#define max_height 60.0	// black value
#define min_height 0
void main(void)
{
	vec4 newVertexPos;
	vec4 dh;
	vec4 dt;
	float du;
	float dv;
	float df;

	// convert real world coordinate to texture coordinate
	du = (gl_Vertex.x / (plane_size))+0.5; 
	dv = (gl_Vertex.y / (plane_size))+0.5;
//	vec2 uv = vec2(du, dv);
	vec2 uv = vec2((gl_MultiTexCoord0.x), 1 - (gl_MultiTexCoord0.y));
	gl_TexCoord[0].x = du; // tile texture 20 times
	gl_TexCoord[0].y = dv;
	gl_TexCoord[0].xy = uv;


//    dh = texture2D( displacementMap, uv);
    dh = tex2D_bilinear( displacementMap, uv);
    dt = texture2D( displacementMap2, gl_MultiTexCoord0.xy);
	
	df = max_height - dh.z*max_height + 0.8;// + dt.z*5;
//	df = dh.z * 100+40;
	newVertexPos = vec4(gl_Normal * df, 0.0) + gl_Vertex;
	newVertexPos = gl_Vertex;
	newVertexPos.z = df;
	gl_Position = gl_ModelViewProjectionMatrix *  newVertexPos;
}
