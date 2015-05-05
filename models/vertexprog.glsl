//GLSL
uniform sampler2D ground;
uniform sampler2D snow;
uniform sampler2D tracks;
uniform vec4 snowHeight;
uniform vec4 pos;
attribute float InstanceID;
//uniform float INSTANCEID;

#define textureSize 512.0
#define texelSize 1.0 / 512.0

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
	vec4 dsnow;
	vec4 dtracks;
	vec4 dground;
	float df;
	gl_TexCoord[0].xy = gl_MultiTexCoord0.xy;
	gl_TexCoord[1].xy = gl_MultiTexCoord0.xy;
	
	vec4 realcoord = ((((256*(gl_Vertex + pos) /100)-2) /256)+1)/256;
	gl_TexCoord[0].xy = realcoord.xy;
    /*
    dsnow = tex2D_bilinear( snow, gl_MultiTexCoord0.xy);
    dground = tex2D_bilinear( ground, realcoord.xy);
    dtracks = tex2D_bilinear( tracks, gl_MultiTexCoord0.xy);
	*/
    dsnow = texture2D(snow, gl_MultiTexCoord0.xy);
    dground = texture2D(ground, realcoord.xy);
    dtracks = texture2D(tracks, gl_MultiTexCoord0.xy);

	if (dtracks.z == 0) {
		df = dground.z + dsnow.z + dtracks.x;
	} else {
		df = min(dground.z + (dtracks.z), dground.z + dsnow.z);
	}
	df = dground.z*10 + min(dtracks.x, dsnow.y * dtracks.z);
	newVertexPos = gl_Vertex + pos;
	newVertexPos = vec4(gl_Normal * df, 0.0) + newVertexPos;

	newVertexPos.z = gl_InstanceID * 40;
	gl_Position = gl_ModelViewProjectionMatrix *  newVertexPos;
}
