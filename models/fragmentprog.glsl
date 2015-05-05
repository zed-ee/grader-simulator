//GLSL 
uniform sampler2D colorMap;
uniform sampler2D tracks;
uniform vec4 color;

void main(void)
{
   gl_FragColor = texture2D(colorMap, gl_TexCoord[0].xy) + texture2D(tracks, gl_TexCoord[1].xy) ;
//	gl_FragColor = color;
}
