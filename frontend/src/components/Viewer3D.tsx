import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

export type MeshSource = { kind: 'url'; url: string } | { kind: 'buffer'; buffer: ArrayBuffer }

interface Viewer3DProps {
  source: MeshSource | null
  colorHex?: number
}

export default function Viewer3D({ source, colorHex = 0x38bdf8 }: Viewer3DProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const meshRef = useRef<THREE.Mesh | null>(null)
  const sceneRef = useRef<THREE.Scene | null>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0b1220)
    sceneRef.current = scene

    const camera = new THREE.PerspectiveCamera(
      45,
      container.clientWidth / container.clientHeight,
      0.01,
      1000,
    )
    camera.position.set(4, 3, 6)

    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.setSize(container.clientWidth, container.clientHeight)
    container.appendChild(renderer.domElement)

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.08

    scene.add(new THREE.AmbientLight(0xffffff, 0.6))
    const dirLight = new THREE.DirectionalLight(0xffffff, 1.0)
    dirLight.position.set(5, 8, 6)
    scene.add(dirLight)
    const rimLight = new THREE.DirectionalLight(0x60a5fa, 0.4)
    rimLight.position.set(-6, 2, -4)
    scene.add(rimLight)

    const grid = new THREE.GridHelper(12, 24, 0x334155, 0x1e293b)
    scene.add(grid)

    let frameId = 0
    const animate = () => {
      frameId = requestAnimationFrame(animate)
      controls.update()
      renderer.render(scene, camera)
    }
    animate()

    const handleResize = () => {
      if (!container) return
      camera.aspect = container.clientWidth / container.clientHeight
      camera.updateProjectionMatrix()
      renderer.setSize(container.clientWidth, container.clientHeight)
    }
    const resizeObserver = new ResizeObserver(handleResize)
    resizeObserver.observe(container)

    return () => {
      cancelAnimationFrame(frameId)
      resizeObserver.disconnect()
      controls.dispose()
      renderer.dispose()
      container.removeChild(renderer.domElement)
    }
  }, [])

  useEffect(() => {
    const scene = sceneRef.current
    if (!scene || !source) return

    const loader = new STLLoader()

    const onGeometry = (geometry: THREE.BufferGeometry) => {
      if (meshRef.current) {
        scene.remove(meshRef.current)
        meshRef.current.geometry.dispose()
        ;(meshRef.current.material as THREE.Material).dispose()
      }

      geometry.computeVertexNormals()
      geometry.computeBoundingBox()
      const box = geometry.boundingBox!
      const size = new THREE.Vector3()
      box.getSize(size)
      const center = new THREE.Vector3()
      box.getCenter(center)
      // STL 좌표계: x=길이, y=폭, z=높이. 길이/폭은 중앙 정렬, 높이는 바닥(z=0)에 맞춘다.
      geometry.translate(-center.x, -center.y, -box.min.z)

      const material = new THREE.MeshStandardMaterial({
        color: colorHex,
        metalness: 0.35,
        roughness: 0.45,
        side: THREE.DoubleSide,
      })
      const mesh = new THREE.Mesh(geometry, material)
      mesh.rotation.x = -Math.PI / 2 // STL z-up -> three.js y-up
      scene.add(mesh)
      meshRef.current = mesh
    }

    if (source.kind === 'url') {
      loader.load(source.url, onGeometry)
    } else {
      const geometry = loader.parse(source.buffer)
      onGeometry(geometry)
    }
  }, [source, colorHex])

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
}
