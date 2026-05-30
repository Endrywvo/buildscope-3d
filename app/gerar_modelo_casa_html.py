#!/usr/bin/env python3
"""Gera o HTML da casa 3D (Three.js) e a planilha de controle."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import casa3d_common as cc

MODULOS = [
    ("MOD-001", "Fundação", "Base", 1, 1, "CONCLUIDO"),
    ("MOD-002", "Piso", "Base", 1, 2, "CONCLUIDO"),
    ("MOD-003", "Parede frontal", "Estrutura", 2, 2, "EM ANDAMENTO"),
    ("MOD-004", "Parede traseira", "Estrutura", 2, 4, "EM ANDAMENTO"),
    ("MOD-005", "Parede lateral esquerda", "Estrutura", 2, 1, "NAO INICIADO"),
    ("MOD-006", "Parede lateral direita", "Estrutura", 2, 5, "NAO INICIADO"),
    ("MOD-007", "Telhado esquerdo", "Cobertura", 3, 1, "PENDENTE"),
    ("MOD-008", "Telhado direito", "Cobertura", 3, 3, "PENDENTE"),
    ("MOD-009", "Porta", "Acesso", 2, 2, "INSPECIONAR"),
    ("MOD-010", "Janela frontal", "Aberturas", 2, 3, "CONCLUIDO"),
    ("MOD-011", "Janela lateral", "Aberturas", 2, 5, "EM ANDAMENTO"),
    ("MOD-012", "Garagem", "Anexo", 1, 5, "BLOQUEADO"),
    ("MOD-013", "Chaminé", "Detalhes", 4, 3, "NAO INICIADO"),
    ("MOD-014", "Varanda", "Exterior", 1, 3, "EM ANDAMENTO"),
    ("MOD-015", "Jardim", "Exterior", 1, 4, "CONCLUIDO"),
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Casa 3D — Demonstração</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { overflow: hidden; background: #87CEEB; font-family: system-ui, sans-serif; }
  #info { position: fixed; top: 12px; left: 12px; background: rgba(255,255,255,0.92);
    padding: 10px 14px; border-radius: 8px; font-size: 13px; z-index: 10; max-width: 280px; }
  #info h1 { font-size: 16px; margin-bottom: 4px; }
</style>
</head>
<body>
<div id="info">
  <h1>Casa 3D</h1>
  <p>Acompanhamento visual de módulos</p>
</div>
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script>
(function() {
  const DEFAULT = 0xcccccc;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87CEEB);
  scene.fog = new THREE.Fog(0x87CEEB, 20, 80);

  const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(12, 10, 14);
  camera.lookAt(0, 2, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  document.body.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.55));
  const sun = new THREE.DirectionalLight(0xffffff, 0.85);
  sun.position.set(10, 20, 10);
  scene.add(sun);

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(40, 40),
    new THREE.MeshLambertMaterial({ color: 0x5a8f4a })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.01;
  scene.add(ground);

  window.modulosCasa = {};
  const defaultColors = {};

  function addModulo(id, geo, matProps, pos, rot) {
    const mat = new THREE.MeshLambertMaterial({ color: DEFAULT, ...matProps });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(pos[0], pos[1], pos[2]);
    if (rot) mesh.rotation.set(rot[0] || 0, rot[1] || 0, rot[2] || 0);
    mesh.userData.moduloId = id;
    scene.add(mesh);
    window.modulosCasa[id] = mesh;
    defaultColors[id] = mat.color.getHex();
    return mesh;
  }

  addModulo("MOD-001", new THREE.BoxGeometry(10, 0.4, 8), {}, [0, 0.2, 0]);
  addModulo("MOD-002", new THREE.BoxGeometry(9, 0.15, 7), {}, [0, 0.45, 0]);
  addModulo("MOD-003", new THREE.BoxGeometry(9, 3, 0.25), {}, [0, 1.9, -3.5]);
  addModulo("MOD-004", new THREE.BoxGeometry(9, 3, 0.25), {}, [0, 1.9, 3.5]);
  addModulo("MOD-005", new THREE.BoxGeometry(0.25, 3, 7), {}, [-4.5, 1.9, 0]);
  addModulo("MOD-006", new THREE.BoxGeometry(0.25, 3, 7), {}, [4.5, 1.9, 0]);
  addModulo("MOD-007", new THREE.BoxGeometry(5.2, 0.2, 7.5), {}, [-2.5, 3.5, 0], [0, 0, 0.35]);
  addModulo("MOD-008", new THREE.BoxGeometry(5.2, 0.2, 7.5), {}, [2.5, 3.5, 0], [0, 0, -0.35]);
  addModulo("MOD-009", new THREE.BoxGeometry(1.2, 2.2, 0.15), { color: 0x8B4513 }, [-1, 1.5, -3.4]);
  addModulo("MOD-010", new THREE.BoxGeometry(1.5, 1, 0.12), { color: 0xADD8E6, transparent: true, opacity: 0.85 }, [1.5, 2, -3.4]);
  addModulo("MOD-011", new THREE.BoxGeometry(0.12, 1, 1.2), { color: 0xADD8E6, transparent: true, opacity: 0.85 }, [4.4, 2, 1]);
  addModulo("MOD-012", new THREE.BoxGeometry(3, 2.5, 4), {}, [6, 1.3, 2]);
  addModulo("MOD-013", new THREE.BoxGeometry(0.6, 1.2, 0.6), { color: 0x696969 }, [2, 4.2, 1]);
  addModulo("MOD-014", new THREE.BoxGeometry(3, 0.15, 2), { color: 0xDEB887 }, [-3, 0.55, -2]);
  addModulo("MOD-015", new THREE.BoxGeometry(4, 0.3, 3), { color: 0x228B22 }, [-3, 0.15, 3.5]);

  function parseColor(c) {
    if (typeof c === "number") return c;
    if (typeof c === "string") {
      if (c.startsWith("#")) return parseInt(c.slice(1), 16);
      if (c.startsWith("rgb")) {
        const m = c.match(/\\d+/g);
        if (m) return (parseInt(m[0]) << 16) + (parseInt(m[1]) << 8) + parseInt(m[2]);
      }
    }
    return DEFAULT;
  }

  window.setModuloColor = function(id, color) {
    const mesh = window.modulosCasa[id];
    if (mesh && mesh.material) {
      mesh.material.color.setHex(parseColor(color));
      mesh.material.needsUpdate = true;
    }
  };

  window.resetModuloColors = function() {
    for (const [id, mesh] of Object.entries(window.modulosCasa)) {
      if (mesh.material) mesh.material.color.setHex(defaultColors[id] || DEFAULT);
    }
  };

  function fitBox(ids) {
    const box = new THREE.Box3();
    ids.forEach(id => {
      const m = window.modulosCasa[id];
      if (m) box.expandByObject(m);
    });
    if (box.isEmpty()) return;
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const dist = maxDim * 2.2;
    camera.position.set(center.x + dist * 0.7, center.y + dist * 0.5, center.z + dist * 0.7);
    camera.lookAt(center);
  }

  window.focusModulo = function(id) { fitBox([id]); };
  window.focusModulos = function(ids) { fitBox(ids); };

  window.resetCamera = function() {
    camera.position.set(12, 10, 14);
    camera.lookAt(0, 2, 0);
  };

  function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  window.captureReady = true;
})();
</script>
</body>
</html>
"""


def gerar_html() -> Path:
    cc.ENTRADA_DIR.mkdir(parents=True, exist_ok=True)
    cc.HTML_CASA.write_text(HTML_TEMPLATE, encoding="utf-8")
    return cc.HTML_CASA


def gerar_planilha() -> Path:
    linhas = []
    for mod_id, nome, grupo, linha, coluna, status in MODULOS:
        info = cc.info_status(status)
        linhas.append({
            "ID_MODULO": mod_id,
            "NOME_MODULO": nome,
            "GRUPO": grupo,
            "STATUS": status,
            "COR_STATUS": info["nome_cor"],
            "DESCRICAO_STATUS": info["descricao"],
            "LINHA_MAPA": linha,
            "COLUNA_MAPA": coluna,
            "OBSERVACAO": "",
            "MANTER_NO_CONTROLE": "SIM",
        })
    df = pd.DataFrame(linhas)
    cc.ENTRADA_DIR.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(cc.EXCEL_CONTROLE, engine="openpyxl") as w:
        df.to_excel(w, sheet_name=cc.ABA_EXCEL, index=False)
    return cc.EXCEL_CONTROLE


def main() -> None:
    html = gerar_html()
    xlsx = gerar_planilha()
    print(f"HTML: {html}")
    print(f"Planilha: {xlsx}")


if __name__ == "__main__":
    main()
