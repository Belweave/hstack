const VERT = `#version 300 es
layout(location=0) in vec2 aPos;
layout(location=1) in vec2 aUv;
out vec2 vUv;
void main() {
  vUv = aUv;
  gl_Position = vec4(aPos, 0.0, 1.0);
}
`;

const FRAG = `#version 300 es
precision highp float;
in vec2 vUv;
uniform float uSeed;
uniform float uTime;
uniform float uHover;
uniform float uMode;
uniform vec2 uSize;
out vec4 frag;

void main() {
  if (uMode < 0.5) {
    vec2 q = (vUv - 0.5) * vec2(1.15, 0.72);
    float d = length(q);
    float a = smoothstep(0.52, 0.12, d) * 0.22;
    vec3 ink = vec3(0.22, 0.16, 0.10);
    frag = vec4(ink * a, a);
    return;
  }

  vec2 p = vUv * 2.0 - 1.0;
  float rad = min(uSize.y * 0.5, 18.0);
  vec2 box = uSize * 0.5;
  vec2 q = abs(p * box) - (box - rad);
  float sdf = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - rad;
  if (sdf > 0.6) discard;

  float edge = smoothstep(-16.0, 0.5, sdf);
  float film = vUv.x * 1.35 + vUv.y * 0.45 + uSeed * 0.23 + uTime * 0.05;
  vec3 irid = 0.58 + 0.42 * cos(6.2831853 * (vec3(film) + vec3(0.0, 0.33, 0.66)));
  vec3 frost = vec3(0.965, 0.955, 0.94);
  vec3 col = mix(frost, irid, 0.34 + edge * 0.5);
  float streak = sin((p.x + uSeed) * 7.0 + uTime * 0.35);
  col += irid * smoothstep(0.2, 1.0, streak) * 0.12;
  col += vec3(1.0, 0.99, 0.96) * smoothstep(0.35, 0.0, vUv.y) * 0.18;
  col *= mix(0.88, 1.0, smoothstep(0.95, 0.4, vUv.y));
  col = mix(col, vec3(1.0), uHover * 0.05);
  float alpha = (0.8 + edge * 0.12 + uHover * 0.04) * smoothstep(0.6, -0.8, sdf);
  frag = vec4(col * alpha, alpha);
}
`;

function compile(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    gl.deleteShader(shader);
    return null;
  }
  return shader;
}

export function mountGlass(stage) {
  const canvas = stage.querySelector("canvas");
  const gl = canvas.getContext("webgl2", {
    alpha: true,
    antialias: true,
    premultipliedAlpha: true,
    powerPreference: "high-performance",
  });
  if (!gl) return null;

  const vs = compile(gl, gl.VERTEX_SHADER, VERT);
  const fs = compile(gl, gl.FRAGMENT_SHADER, FRAG);
  if (!vs || !fs) return null;
  const program = gl.createProgram();
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return null;

  const buffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.useProgram(program);
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
  const loc = {
    seed: gl.getUniformLocation(program, "uSeed"),
    time: gl.getUniformLocation(program, "uTime"),
    hover: gl.getUniformLocation(program, "uHover"),
    mode: gl.getUniformLocation(program, "uMode"),
    size: gl.getUniformLocation(program, "uSize"),
  };

  const plates = () => [...stage.querySelectorAll(".plate")];

  function draw(time, hoverIndex) {
    const cssW = stage.clientWidth;
    const cssH = stage.clientHeight;
    if (cssW < 2 || cssH < 2) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 1.75);
    const w = Math.round(cssW * dpr);
    const h = Math.round(cssH * dpr);
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
    gl.viewport(0, 0, w, h);
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);

    const box = stage.getBoundingClientRect();
    const list = plates();
    const rects = list.map((plate) => {
      const r = plate.getBoundingClientRect();
      return {
        x: (r.left - box.left) * dpr,
        y: (r.top - box.top) * dpr,
        w: r.width * dpr,
        h: r.height * dpr,
      };
    });

    const union = rects.reduce(
      (acc, r) => ({
        x: Math.min(acc.x, r.x),
        y: Math.min(acc.y, r.y),
        r: Math.max(acc.r, r.x + r.w),
        b: Math.max(acc.b, r.y + r.h),
      }),
      { x: w, y: h, r: 0, b: 0 },
    );
    drawQuad(gl, buffer, loc, union.x - 24 * dpr, union.b - 8 * dpr, union.r - union.x + 48 * dpr, 54 * dpr, w, h, {
      mode: 0,
      seed: 0,
      time,
      hover: 0,
    });

    for (let i = rects.length - 1; i >= 0; i -= 1) {
      const r = rects[i];
      const padX = 6 * dpr;
      const padY = 1.5 * dpr;
      drawQuad(gl, buffer, loc, r.x - padX, r.y - padY, r.w + padX * 2, r.h + padY * 2, w, h, {
        mode: 1,
        seed: i * 1.37,
        time,
        hover: hoverIndex === i ? 1 : 0,
      });
    }
  }

  return { draw };
}

function drawQuad(gl, buffer, loc, x, y, bw, bh, w, h, style) {
  const x0 = (x / w) * 2 - 1;
  const x1 = ((x + bw) / w) * 2 - 1;
  const y0 = 1 - (y / h) * 2;
  const y1 = 1 - ((y + bh) / h) * 2;
  const data = new Float32Array([
    x0, y0, 0, 0,
    x1, y0, 1, 0,
    x0, y1, 0, 1,
    x0, y1, 0, 1,
    x1, y0, 1, 0,
    x1, y1, 1, 1,
  ]);
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW);
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 16, 0);
  gl.enableVertexAttribArray(1);
  gl.vertexAttribPointer(1, 2, gl.FLOAT, false, 16, 8);
  gl.uniform1f(loc.mode, style.mode);
  gl.uniform1f(loc.seed, style.seed);
  gl.uniform1f(loc.time, style.time);
  gl.uniform1f(loc.hover, style.hover);
  gl.uniform2f(loc.size, bw, bh);
  gl.drawArrays(gl.TRIANGLES, 0, 6);
}
