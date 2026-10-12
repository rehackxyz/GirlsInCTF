import cv2
import cma
import numpy as np
from insightface.app import FaceAnalysis
from insightface.utils import face_align

# ============================================================
# Configuration
# ============================================================

SEED_IMAGE = "man3.png"
TARGET_NPY = "my_face.npy"

OUTPUT_IMAGE = "final_cma.png"
BEST_FACE_IMAGE = "best_cma_face.png"

# CMA-ES
PERTURB_SIZE = 24
POPULATION = 64
MAX_GENERATIONS = 300
CMA_SIGMA = 3.0
PIXEL_DELTA = 30

TARGET_SCORE = 0.90

# Reproducibility
SEED = 1337

# ============================================================
# Random seed
# ============================================================

np.random.seed(SEED)

# ============================================================
# Initialize InsightFace
# ============================================================

print("[+] Loading InsightFace...")

app = FaceAnalysis(name="buffalo_l")

# Change to ctx_id=0 if your GPU is device 0.
app.prepare(
    ctx_id=1,
    det_size=(640, 640)
)

rec_model = app.models["recognition"]

input_size = rec_model.input_size

if isinstance(input_size, (tuple, list)):
    input_size = input_size[0]

print(f"[+] Recognition input size: {input_size}x{input_size}")

# ============================================================
# Load target embedding
# ============================================================

print("[+] Loading target embedding...")

target = np.load(TARGET_NPY).astype(np.float32)

target_norm = np.linalg.norm(target)

if target_norm == 0:
    raise RuntimeError("Target embedding has zero norm")

target /= target_norm

print(f"[+] Target embedding shape: {target.shape}")

# ============================================================
# Load seed image
# ============================================================

seed_img = cv2.imread(SEED_IMAGE)

if seed_img is None:
    raise RuntimeError(
        f"Cannot load seed image: {SEED_IMAGE}"
    )

print(
    f"[+] Seed image: "
    f"{seed_img.shape[1]}x{seed_img.shape[0]}"
)

# ============================================================
# Detect face once
# ============================================================

print("[+] Detecting face...")

faces = app.get(seed_img)

if not faces:
    raise RuntimeError("No face detected")

# Use largest face if multiple faces are detected.
face = max(
    faces,
    key=lambda f: (
        (f.bbox[2] - f.bbox[0]) *
        (f.bbox[3] - f.bbox[1])
    )
)

bbox = face.bbox.astype(int)

x1, y1, x2, y2 = bbox

# Clamp bounding box
x1 = max(0, x1)
y1 = max(0, y1)
x2 = min(seed_img.shape[1], x2)
y2 = min(seed_img.shape[0], y2)

print(
    f"[+] Face bbox: "
    f"({x1}, {y1}) -> ({x2}, {y2})"
)

# ============================================================
# Align face
# ============================================================

print("[+] Aligning face...")

aligned = face_align.norm_crop(
    seed_img,
    landmark=face.kps,
    image_size=input_size
)

aligned = aligned.astype(np.uint8)

if aligned.shape[:2] != (input_size, input_size):
    aligned = cv2.resize(
        aligned,
        (input_size, input_size),
        interpolation=cv2.INTER_LINEAR
    )

# Save original aligned face
cv2.imwrite(
    "original_aligned.png",
    aligned
)

# Keep float version for optimization
base_image = aligned.astype(np.float32)

# ============================================================
# Embedding helper
# ============================================================

def get_embedding(image):
    """
    Calculate normalized ArcFace embedding.
    """

    emb = rec_model.get_feat([image])[0]

    emb = emb.astype(np.float32)

    norm = np.linalg.norm(emb)

    if norm == 0:
        return emb

    return emb / norm


# ============================================================
# Initial score
# ============================================================

print("[+] Calculating initial score...")

initial_emb = get_embedding(aligned)

initial_score = float(
    initial_emb @ target
)

print(
    f"[+] Initial cosine similarity: "
    f"{initial_score:.6f}"
)

# ============================================================
# Low-dimensional perturbation
# ============================================================
#
# Instead of optimizing:
#
#     112 * 112 * 3 = 37,632 variables
#
# we optimize:
#
#     16 * 16 * 3 = 768 variables
#
# and upscale the perturbation to 112x112.
#
# ============================================================

VARIABLES = (
    PERTURB_SIZE *
    PERTURB_SIZE *
    3
)

print(
    f"[+] CMA-ES variables: {VARIABLES}"
)

# ============================================================
# Render perturbation
# ============================================================

def render_candidate(x):
    """
    Convert a CMA-ES vector into a 112x112 image.
    """

    delta = np.asarray(
        x,
        dtype=np.float32
    ).reshape(
        PERTURB_SIZE,
        PERTURB_SIZE,
        3
    )

    # Restrict perturbation
    delta = PIXEL_DELTA * np.tanh(delta / PIXEL_DELTA)

    # Upscale perturbation
    delta = cv2.resize(
        delta,
        (input_size, input_size),
        interpolation=cv2.INTER_LINEAR
    )

    # Apply perturbation
    result = base_image + delta

    # Valid image range
    result = np.clip(
        result,
        0,
        255
    )

    return result.astype(np.uint8)


# ============================================================
# Batch evaluation
# ============================================================

def evaluate_population(solutions):
    """
    Evaluate a population using one batched
    InsightFace recognition call.
    """

    images = []

    for solution in solutions:

        img = render_candidate(solution)

        images.append(img)

    # One GPU batch
    embeddings = rec_model.get_feat(images)

    embeddings = embeddings.astype(
        np.float32
    )

    # Normalize
    norms = np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True
    )

    norms = np.maximum(
        norms,
        1e-12
    )

    embeddings /= norms

    # Cosine similarity
    scores = embeddings @ target

    return scores


# ============================================================
# CMA-ES initialization
# ============================================================

print("[+] Initializing CMA-ES...")

x0 = np.zeros(
    VARIABLES,
    dtype=np.float64
)

options = {
    "popsize": POPULATION,

    "maxiter": MAX_GENERATIONS,

    # Keep CMA-ES deterministic
    "seed": SEED,

    # Don't print CMA-ES's own verbose output.
    "verbose": -9,

    # CMA-ES stopping criteria
    "tolfun": 1e-8,
    "tolx": 1e-8,
}

es = cma.CMAEvolutionStrategy(
    x0,
    CMA_SIGMA,
    options
)

# ============================================================
# Optimization state
# ============================================================

best_score = initial_score

best_solution = np.zeros(
    VARIABLES,
    dtype=np.float32
)

best_image = aligned.copy()

total_evaluations = 0

# ============================================================
# CMA-ES optimization
# ============================================================

print("[+] Starting CMA-ES...")
print()

for generation in range(MAX_GENERATIONS):

    # --------------------------------------------------------
    # Generate candidate population
    # --------------------------------------------------------

    solutions = es.ask()

    # --------------------------------------------------------
    # Evaluate candidates in one GPU batch
    # --------------------------------------------------------

    scores = evaluate_population(
        solutions
    )

    total_evaluations += len(scores)

    # --------------------------------------------------------
    # CMA-ES minimizes by default.
    #
    # We want to MAXIMIZE cosine similarity.
    #
    # Therefore:
    #
    #     objective = -cosine_similarity
    # --------------------------------------------------------

    objectives = [
        -float(score)
        for score in scores
    ]

    es.tell(
        solutions,
        objectives
    )

    # --------------------------------------------------------
    # Find best candidate in this generation
    # --------------------------------------------------------

    best_idx = int(
        np.argmax(scores)
    )

    generation_score = float(
        scores[best_idx]
    )

    # --------------------------------------------------------
    # Update global best
    # --------------------------------------------------------

    if generation_score > best_score:

        best_score = generation_score

        best_solution = np.asarray(
            solutions[best_idx],
            dtype=np.float32
        ).copy()

        best_image = render_candidate(
            best_solution
        )

        print(
            f"[+] generation={generation:04d} "
            f"score={best_score:.6f} "
            f"evaluations={total_evaluations}"
        )

        # Save intermediate result
        cv2.imwrite(
            BEST_FACE_IMAGE,
            best_image
        )

    # --------------------------------------------------------
    # Stop if target reached
    # --------------------------------------------------------

    if best_score >= TARGET_SCORE:

        print()
        print(
            f"[+] Target score reached: "
            f"{best_score:.6f}"
        )

        break

    # --------------------------------------------------------
    # Periodic progress
    # --------------------------------------------------------

    if generation % 25 == 0:

        print(
            f"[*] generation={generation:04d} "
            f"current={generation_score:.6f} "
            f"best={best_score:.6f} "
            f"sigma={es.sigma:.4f}"
        )

# ============================================================
# Final verification
# ============================================================

print()
print("[+] Performing final verification...")

final_emb = get_embedding(
    best_image
)

final_score = float(
    final_emb @ target
)

print(
    f"[+] Final cosine similarity: "
    f"{final_score:.6f}"
)

# ============================================================
# Reconstruct optimized face correctly
# ============================================================

# ArcFace 112x112 landmark template.
#
# These are the standard InsightFace / ArcFace landmarks:
#
# left eye
# right eye
# nose
# left mouth
# right mouth

ARC_FACE_TEMPLATE = np.array(
    [
        [38.2946, 51.6963],
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041],
    ],
    dtype=np.float32
)


# ------------------------------------------------------------
# Calculate transform:
#
# original image landmarks
#          ->
# 112x112 ArcFace landmarks
# ------------------------------------------------------------

src_landmarks = face.kps.astype(np.float32)

dst_landmarks = ARC_FACE_TEMPLATE.copy()

M, inliers = cv2.estimateAffinePartial2D(
    src_landmarks,
    dst_landmarks,
    method=cv2.LMEDS
)

if M is None:
    raise RuntimeError(
        "Could not calculate face alignment matrix"
    )

print("[+] Alignment matrix:")
print(M)


# ------------------------------------------------------------
# Invert transformation
#
# 112x112 aligned face
#          ->
# original image coordinates
# ------------------------------------------------------------

M_inv = cv2.invertAffineTransform(M)


# ------------------------------------------------------------
# Warp optimized face back into original image
# ------------------------------------------------------------

H, W = seed_img.shape[:2]

warped_face = cv2.warpAffine(
    best_image,
    M_inv,
    (W, H),
    flags=cv2.INTER_LINEAR,
    borderMode=cv2.BORDER_CONSTANT,
    borderValue=(0, 0, 0)
)


# ------------------------------------------------------------
# Create mask
#
# We don't want to paste the entire rectangular 112x112
# image back into the original.
#
# Use a soft elliptical/face-shaped mask.
# ------------------------------------------------------------

mask_112 = np.zeros(
    (input_size, input_size),
    dtype=np.uint8
)

center = (
    input_size // 2,
    input_size // 2
)

axes = (
    int(input_size * 0.43),
    int(input_size * 0.48)
)

cv2.ellipse(
    mask_112,
    center,
    axes,
    0,
    0,
    360,
    255,
    -1
)


# Feather mask edges
mask_112 = cv2.GaussianBlur(
    mask_112,
    (21, 21),
    0
)


# Warp mask back to original coordinates
warped_mask = cv2.warpAffine(
    mask_112,
    M_inv,
    (W, H),
    flags=cv2.INTER_LINEAR,
    borderMode=cv2.BORDER_CONSTANT,
    borderValue=0
)


# ------------------------------------------------------------
# Alpha composite
# ------------------------------------------------------------

alpha = (
    warped_mask.astype(np.float32) / 255.0
)

alpha = alpha[..., None]

original_float = (
    seed_img.astype(np.float32)
)

warped_float = (
    warped_face.astype(np.float32)
)

final = (
    warped_float * alpha
    +
    original_float * (1.0 - alpha)
)

final = np.clip(
    final,
    0,
    255
).astype(np.uint8)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

cv2.imwrite(
    OUTPUT_IMAGE,
    final
)

cv2.imwrite(
    BEST_FACE_IMAGE,
    best_image
)

print(
    f"[+] Saved reconstructed image: "
    f"{OUTPUT_IMAGE}"
)