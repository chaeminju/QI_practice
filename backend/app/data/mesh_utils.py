"""
간단한 2D 측면 실루엣 폴리곤을 3D 프리즘으로 압출(extrude)해 더미 STL을
생성하기 위한 유틸리티. 실제 CAD 데이터가 아닌, 3D 뷰어 데모용 목업 지오메트리다.
"""
from typing import List, Tuple

import numpy as np

Point2D = Tuple[float, float]


def _cross(o: Point2D, a: Point2D, b: Point2D) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _point_in_triangle(p: Point2D, a: Point2D, b: Point2D, c: Point2D) -> bool:
    d1 = _cross(p, a, b)
    d2 = _cross(p, b, c)
    d3 = _cross(p, c, a)
    has_neg = d1 < 0 or d2 < 0 or d3 < 0
    has_pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (has_neg and has_pos)


def triangulate_polygon(points: List[Point2D]) -> List[Tuple[int, int, int]]:
    """단순 다각형(비자기교차)에 대한 ear-clipping 삼각분할."""
    n = len(points)
    idx = list(range(n))

    area = 0.0
    for i in range(n):
        x1, y1 = points[idx[i]]
        x2, y2 = points[idx[(i + 1) % n]]
        area += x1 * y2 - x2 * y1
    if area < 0:
        idx.reverse()

    triangles: List[Tuple[int, int, int]] = []
    guard = 0
    while len(idx) > 3 and guard < 20000:
        guard += 1
        ear_found = False
        m = len(idx)
        for i in range(m):
            i_prev = idx[(i - 1) % m]
            i_curr = idx[i]
            i_next = idx[(i + 1) % m]
            a, b, c = points[i_prev], points[i_curr], points[i_next]
            if _cross(a, b, c) <= 1e-9:
                continue
            contains_other = False
            for j in idx:
                if j in (i_prev, i_curr, i_next):
                    continue
                if _point_in_triangle(points[j], a, b, c):
                    contains_other = True
                    break
            if not contains_other:
                triangles.append((i_prev, i_curr, i_next))
                idx.pop(i)
                ear_found = True
                break
        if not ear_found:
            break
    if len(idx) == 3:
        triangles.append((idx[0], idx[1], idx[2]))
    return triangles


def extrude_polygon(profile_xz: List[Point2D], width: float) -> Tuple[np.ndarray, np.ndarray]:
    """profile_xz(측면 실루엣, x=길이축 z=높이축)를 y축(폭) 방향으로 압출한다."""
    n = len(profile_xz)
    front = [(x, 0.0, z) for x, z in profile_xz]
    back = [(x, width, z) for x, z in profile_xz]
    vertices = np.array(front + back, dtype=np.float32)

    tris_2d = triangulate_polygon(profile_xz)
    faces = []
    for a, b, c in tris_2d:
        faces.append((a, c, b))
    for a, b, c in tris_2d:
        faces.append((a + n, b + n, c + n))
    for i in range(n):
        i2 = (i + 1) % n
        f0, f1 = i, i2
        b0, b1 = i + n, i2 + n
        faces.append((f0, f1, b1))
        faces.append((f0, b1, b0))

    return vertices, np.array(faces, dtype=np.int64)


def save_stl(vertices: np.ndarray, faces: np.ndarray, path: str) -> None:
    from stl import mesh as stl_mesh

    m = stl_mesh.Mesh(np.zeros(faces.shape[0], dtype=stl_mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            m.vectors[i][j] = vertices[f[j], :]
    m.save(path)
