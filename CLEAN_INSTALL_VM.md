# Clean install on a fresh Linux VM

Date: 2026-10-26 UTC.
OS: Ubuntu 24.04.4 LTS, Linux 7.0.0-1014-aws, x86_64.
Python: 3.13.18. The image's default `python3` was 3.12.3, so Python 3.13 was installed first so the README command `python3.13` could run as written.
Repository: the current working tree, copied in place of a git clone. No `.git` directory and no private log.

## Result

The README Linux install commands completed: new venv, CPU torch, ComfyUI clone and checkout `87ed5a066d9c4660ef42100fd01a888da6994856`, ComfyUI requirements, `pip install` of this project, and the custom-node copy. Exit codes are in the transcript.

The app was then started from the repository, which is where the README puts `python -m shotcheck app`.

- The process printed a localhost URL and the abstention line.
- `GET /` returned HTTP 200.
- `POST /api/check` with the bundled `examples/synthetic_tilt_up.avi` and intent `tilt_up` returned HTTP 200.
- Verdict: MATCH. Measured `scene_down`. Expected `scene_down`. Counts: 4 match, 0 mismatch, 0 inconclusive. Each window confidence was 1.0.
- The same clip and intent on the development machine returned that same verdict.

The ComfyUI server process, the proxy, and `shotcheck run` were not the recorded check.

## First app start, and why it was repeated

The first start was launched in the parent of the repository. It exited immediately: `No module named shotcheck.__main__`. From that parent, the repository directory is itself a package, because the ComfyUI entry `__init__.py` lives at the repository root. The README says to run the app from the repository. The retry did that, and it is the result above.

## Transcript

The install transcript follows. Home directories are written as `<vm-user>`.

```
=== OS ===
Linux 7.0.0-1014-aws x86_64
Ubuntu 24.04.4 LTS
=== PYTHON ===
Python 3.13.18
=== STEP venv ===
venv_exit:0
=== STEP torch ===
Looking in indexes: https://download.pytorch.org/whl/cpu
Collecting torch
  Downloading torch-2.14.1%2Bcpu-cp313-cp313-manylinux_2_28_x86_64.whl.metadata (37 kB)
Collecting torchvision
  Downloading torchvision-0.29.1%2Bcpu-cp313-cp313-manylinux_2_28_x86_64.whl.metadata (5.7 kB)
Collecting filelock (from torch)
  Downloading filelock-3.32.3-py3-none-any.whl.metadata (2.0 kB)
Collecting typing-extensions>=4.10.0 (from torch)
  Using cached typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
Collecting setuptools>=77.0.3 (from torch)
  Downloading setuptools-78.1.0-py3-none-any.whl.metadata (6.6 kB)
Collecting sympy>=1.13.3 (from torch)
  Downloading sympy-1.14.0-py3-none-any.whl.metadata (12 kB)
Collecting networkx>=2.5.1 (from torch)
  Downloading networkx-3.6.1-py3-none-any.whl.metadata (6.8 kB)
Collecting jinja2 (from torch)
  Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting fsspec>=0.8.5 (from torch)
  Downloading fsspec-2026.7.0-py3-none-any.whl.metadata (10 kB)
Collecting numpy (from torchvision)
  Downloading numpy-2.5.2-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (6.6 kB)
Collecting pillow!=8.3.*,>=5.3.0 (from torchvision)
  Downloading pillow-12.3.0-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (9.1 kB)
Collecting mpmath<1.4,>=1.1.0 (from sympy>=1.13.3->torch)
  Downloading mpmath-1.3.0-py3-none-any.whl.metadata (8.6 kB)
Collecting MarkupSafe>=2.0 (from jinja2->torch)
  Downloading markupsafe-3.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
Downloading torch-2.14.1%2Bcpu-cp313-cp313-manylinux_2_28_x86_64.whl (196.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 196.3/196.3 MB 38.1 MB/s  0:00:05
Downloading torchvision-0.29.1%2Bcpu-cp313-cp313-manylinux_2_28_x86_64.whl (1.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.7/1.7 MB 98.9 MB/s  0:00:00
Downloading fsspec-2026.7.0-py3-none-any.whl (206 kB)
Downloading networkx-3.6.1-py3-none-any.whl (2.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.1/2.1 MB 59.2 MB/s  0:00:00
Downloading pillow-12.3.0-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (6.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.9/6.9 MB 148.6 MB/s  0:00:00
Downloading setuptools-78.1.0-py3-none-any.whl (1.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 109.0 MB/s  0:00:00
Downloading sympy-1.14.0-py3-none-any.whl (6.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.3/6.3 MB 174.5 MB/s  0:00:00
Downloading mpmath-1.3.0-py3-none-any.whl (536 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 536.2/536.2 kB 42.4 MB/s  0:00:00
Using cached typing_extensions-4.16.0-py3-none-any.whl (45 kB)
Downloading filelock-3.32.3-py3-none-any.whl (98 kB)
Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
Downloading markupsafe-3.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
Downloading numpy-2.5.2-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (16.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 16.7/16.7 MB 120.4 MB/s  0:00:00
Installing collected packages: mpmath, typing-extensions, sympy, setuptools, pillow, numpy, networkx, MarkupSafe, fsspec, filelock, jinja2, torch, torchvision

Successfully installed MarkupSafe-3.0.3 filelock-3.32.3 fsspec-2026.7.0 jinja2-3.1.6 mpmath-1.3.0 networkx-3.6.1 numpy-2.5.2 pillow-12.3.0 setuptools-78.1.0 sympy-1.14.0 torch-2.14.1+cpu torchvision-0.29.1+cpu typing-extensions-4.16.0
torch_exit:0
=== STEP comfy clone ===
Cloning into 'ComfyUI'...
clone_exit:0
Note: switching to '87ed5a066d9c4660ef42100fd01a888da6994856'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

Or undo this operation with:

  git switch -

Turn off this advice by setting config variable advice.detachedHead to false

HEAD is now at 87ed5a06 feat: Add Fibo 2.0 support (#17240)
checkout_exit:0
=== STEP comfy requirements ===
Collecting comfyui-frontend-package==1.57.1 (from -r ComfyUI/requirements.txt (line 1))
  Downloading comfyui_frontend_package-1.57.1-py3-none-any.whl.metadata (117 bytes)
Collecting comfyui-workflow-templates==0.11.93 (from -r ComfyUI/requirements.txt (line 2))
  Downloading comfyui_workflow_templates-0.11.93-py3-none-any.whl.metadata (24 kB)
Collecting comfyui-embedded-docs==0.5.14 (from -r ComfyUI/requirements.txt (line 3))
  Downloading comfyui_embedded_docs-0.5.14-py3-none-any.whl.metadata (5.3 kB)
Requirement already satisfied: torch in ./.venv/lib/python3.13/site-packages (from -r ComfyUI/requirements.txt (line 4)) (2.14.1+cpu)
Collecting torchsde (from -r ComfyUI/requirements.txt (line 5))
  Downloading torchsde-0.2.6-py3-none-any.whl.metadata (5.3 kB)
Requirement already satisfied: torchvision in ./.venv/lib/python3.13/site-packages (from -r ComfyUI/requirements.txt (line 6)) (0.29.1+cpu)
Requirement already satisfied: numpy>=1.25.0 in ./.venv/lib/python3.13/site-packages (from -r ComfyUI/requirements.txt (line 7)) (2.5.2)
Collecting einops (from -r ComfyUI/requirements.txt (line 8))
  Downloading einops-0.8.2-py3-none-any.whl.metadata (13 kB)
Collecting transformers>=4.50.3 (from -r ComfyUI/requirements.txt (line 9))
  Downloading transformers-5.21.0-py3-none-any.whl.metadata (31 kB)
Collecting tokenizers>=0.13.3 (from -r ComfyUI/requirements.txt (line 10))
  Downloading tokenizers-0.23.3-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (9.8 kB)
Collecting sentencepiece (from -r ComfyUI/requirements.txt (line 11))
  Downloading sentencepiece-0.2.2-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (33 kB)
Collecting safetensors>=0.4.2 (from -r ComfyUI/requirements.txt (line 12))
  Downloading safetensors-0.8.0-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.2 kB)
Collecting aiohttp>=3.11.8 (from -r ComfyUI/requirements.txt (line 13))
  Downloading aiohttp-3.14.5-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (8.3 kB)
Collecting yarl>=1.18.0 (from -r ComfyUI/requirements.txt (line 14))
  Downloading yarl-1.25.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (111 kB)
Collecting pyyaml (from -r ComfyUI/requirements.txt (line 15))
  Downloading pyyaml-6.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.4 kB)
Requirement already satisfied: Pillow in ./.venv/lib/python3.13/site-packages (from -r ComfyUI/requirements.txt (line 16)) (12.3.0)
Collecting scipy (from -r ComfyUI/requirements.txt (line 17))
  Downloading scipy-1.18.1-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (62 kB)
Collecting tqdm (from -r ComfyUI/requirements.txt (line 18))
  Using cached tqdm-4.70.1-py3-none-any.whl.metadata (57 kB)
Collecting psutil (from -r ComfyUI/requirements.txt (line 19))
  Downloading psutil-7.2.2-cp36-abi3-manylinux2010_x86_64.manylinux_2_12_x86_64.manylinux_2_28_x86_64.whl.metadata (22 kB)
Collecting alembic (from -r ComfyUI/requirements.txt (line 20))
  Downloading alembic-1.20.1-py3-none-any.whl.metadata (7.3 kB)
Collecting SQLAlchemy>=2.0.0 (from -r ComfyUI/requirements.txt (line 21))
  Downloading sqlalchemy-2.1.6-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (9.7 kB)
Requirement already satisfied: filelock in ./.venv/lib/python3.13/site-packages (from -r ComfyUI/requirements.txt (line 22)) (3.32.3)
Collecting av>=17.0.0 (from -r ComfyUI/requirements.txt (line 23))
  Downloading av-19.0.2-cp312-abi3-manylinux_2_28_x86_64.whl.metadata (5.0 kB)
Collecting comfy-kitchen==0.2.39 (from -r ComfyUI/requirements.txt (line 24))
  Downloading comfy_kitchen-0.2.39-cp312-abi3-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl.metadata (19 kB)
Collecting comfy-aimdo==0.5.6 (from -r ComfyUI/requirements.txt (line 25))
  Downloading comfy_aimdo-0.5.6-cp39-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (4.4 kB)
Collecting requests (from -r ComfyUI/requirements.txt (line 26))
  Downloading requests-2.34.2-py3-none-any.whl.metadata (4.8 kB)
Collecting simpleeval>=1.0.0 (from -r ComfyUI/requirements.txt (line 27))
  Downloading simpleeval-1.0.8-py3-none-any.whl.metadata (20 kB)
Collecting blake3 (from -r ComfyUI/requirements.txt (line 28))
  Downloading blake3-1.0.11-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.9 kB)
Collecting kornia>=0.7.1 (from -r ComfyUI/requirements.txt (line 31))
  Downloading kornia-0.9.0-py3-none-any.whl.metadata (26 kB)
Collecting spandrel (from -r ComfyUI/requirements.txt (line 32))
  Downloading spandrel-0.4.2-py3-none-any.whl.metadata (15 kB)
Collecting pydantic~=2.0 (from -r ComfyUI/requirements.txt (line 33))
  Downloading pydantic-2.14.1-py3-none-any.whl.metadata (133 kB)
Collecting pydantic-settings~=2.0 (from -r ComfyUI/requirements.txt (line 34))
  Downloading pydantic_settings-2.16.1-py3-none-any.whl.metadata (4.0 kB)
Collecting PyOpenGL>=3.1.8 (from -r ComfyUI/requirements.txt (line 35))
  Downloading pyopengl-3.1.10-py3-none-any.whl.metadata (3.3 kB)
Collecting comfy-angle (from -r ComfyUI/requirements.txt (line 36))
  Downloading comfy_angle-0.1.1-py3-none-manylinux_2_28_x86_64.whl.metadata (2.2 kB)
Collecting comfyui-workflow-templates-core==0.3.384 (from comfyui-workflow-templates==0.11.93->-r ComfyUI/requirements.txt (line 2))
  Downloading comfyui_workflow_templates_core-0.3.384-py3-none-any.whl.metadata (260 bytes)
Collecting comfyui-workflow-templates-json==0.1.119 (from comfyui-workflow-templates==0.11.93->-r ComfyUI/requirements.txt (line 2))
  Downloading comfyui_workflow_templates_json-0.1.119-py3-none-any.whl.metadata (266 bytes)
Collecting comfyui-workflow-templates-media-api==0.3.84 (from comfyui-workflow-templates==0.11.93->-r ComfyUI/requirements.txt (line 2))
  Downloading comfyui_workflow_templates_media_api-0.3.84-py3-none-any.whl.metadata (290 bytes)
Collecting comfyui-workflow-templates-media-video==0.3.101 (from comfyui-workflow-templates==0.11.93->-r ComfyUI/requirements.txt (line 2))
  Downloading comfyui_workflow_templates_media_video-0.3.101-py3-none-any.whl.metadata (283 bytes)
Collecting comfyui-workflow-templates-media-image==0.3.160 (from comfyui-workflow-templates==0.11.93->-r ComfyUI/requirements.txt (line 2))
  Downloading comfyui_workflow_templates_media_image-0.3.160-py3-none-any.whl.metadata (283 bytes)
Collecting comfyui-workflow-templates-media-other==0.3.229 (from comfyui-workflow-templates==0.11.93->-r ComfyUI/requirements.txt (line 2))
  Downloading comfyui_workflow_templates_media_other-0.3.229-py3-none-any.whl.metadata (306 bytes)
Collecting comfyui-workflow-templates-media-assets-01==0.1.48 (from comfyui-workflow-templates==0.11.93->-r ComfyUI/requirements.txt (line 2))
  Downloading comfyui_workflow_templates_media_assets_01-0.1.48-py3-none-any.whl.metadata (290 bytes)
Collecting comfyui-workflow-templates-media-assets-02==0.1.20 (from comfyui-workflow-templates==0.11.93->-r ComfyUI/requirements.txt (line 2))
  Downloading comfyui_workflow_templates_media_assets_02-0.1.20-py3-none-any.whl.metadata (290 bytes)
Collecting annotated-types>=0.6.0 (from pydantic~=2.0->-r ComfyUI/requirements.txt (line 33))
  Downloading annotated_types-0.8.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.50.1 (from pydantic~=2.0->-r ComfyUI/requirements.txt (line 33))
  Downloading pydantic_core-2.50.1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.5 kB)
Requirement already satisfied: typing-extensions>=4.16.0 in ./.venv/lib/python3.13/site-packages (from pydantic~=2.0->-r ComfyUI/requirements.txt (line 33)) (4.16.0)
Collecting typing-inspection>=0.4.4 (from pydantic~=2.0->-r ComfyUI/requirements.txt (line 33))
  Downloading typing_inspection-0.4.4-py3-none-any.whl.metadata (2.6 kB)
Collecting python-dotenv>=1.2.2 (from pydantic-settings~=2.0->-r ComfyUI/requirements.txt (line 34))
  Downloading python_dotenv-1.2.4-py3-none-any.whl.metadata (29 kB)
Requirement already satisfied: setuptools>=77.0.3 in ./.venv/lib/python3.13/site-packages (from torch->-r ComfyUI/requirements.txt (line 4)) (78.1.0)
Requirement already satisfied: sympy>=1.13.3 in ./.venv/lib/python3.13/site-packages (from torch->-r ComfyUI/requirements.txt (line 4)) (1.14.0)
Requirement already satisfied: networkx>=2.5.1 in ./.venv/lib/python3.13/site-packages (from torch->-r ComfyUI/requirements.txt (line 4)) (3.6.1)
Requirement already satisfied: jinja2 in ./.venv/lib/python3.13/site-packages (from torch->-r ComfyUI/requirements.txt (line 4)) (3.1.6)
Requirement already satisfied: fsspec>=0.8.5 in ./.venv/lib/python3.13/site-packages (from torch->-r ComfyUI/requirements.txt (line 4)) (2026.7.0)
Collecting trampoline>=0.1.2 (from torchsde->-r ComfyUI/requirements.txt (line 5))
  Downloading trampoline-0.1.2-py3-none-any.whl.metadata (10 kB)
Collecting huggingface-hub<3.0,>=1.31.0 (from transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Using cached huggingface_hub-2.3.0-py3-none-any.whl.metadata (16 kB)
Collecting packaging>=20.0 (from transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Using cached packaging-26.3-py3-none-any.whl.metadata (3.5 kB)
Collecting regex>=2025.10.22 (from transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Downloading regex-2026.9.29-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (40 kB)
Collecting typer (from transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Downloading typer-0.27.3-py3-none-any.whl.metadata (16 kB)
Collecting click<9.0.0,>=8.4.2 (from huggingface-hub<3.0,>=1.31.0->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Using cached click-8.5.0-py3-none-any.whl.metadata (2.6 kB)
Collecting hf-xet<2.0.0,>=1.6.0 (from huggingface-hub<3.0,>=1.31.0->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Using cached hf_xet-1.7.0-cp38-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (4.9 kB)
Collecting httpx2<3,>=2.0.0 (from huggingface-hub<3.0,>=1.31.0->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Using cached httpx2-2.16.0-py3-none-any.whl.metadata (10 kB)
Collecting anyio>=4.10 (from httpx2<3,>=2.0.0->huggingface-hub<3.0,>=1.31.0->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Using cached anyio-4.15.1-py3-none-any.whl.metadata (4.7 kB)
Collecting httpcore2==2.16.0 (from httpx2<3,>=2.0.0->huggingface-hub<3.0,>=1.31.0->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Using cached httpcore2-2.16.0-py3-none-any.whl.metadata (27 kB)
Collecting idna>=3.18 (from httpx2<3,>=2.0.0->huggingface-hub<3.0,>=1.31.0->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Using cached idna-3.20-py3-none-any.whl.metadata (7.2 kB)
Collecting truststore>=0.10 (from httpx2<3,>=2.0.0->huggingface-hub<3.0,>=1.31.0->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Using cached truststore-0.10.5-py3-none-any.whl.metadata (4.5 kB)
Collecting h11>=0.16 (from httpcore2==2.16.0->httpx2<3,>=2.0.0->huggingface-hub<3.0,>=1.31.0->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting aiohappyeyeballs>=2.5.0 (from aiohttp>=3.11.8->-r ComfyUI/requirements.txt (line 13))
  Downloading aiohappyeyeballs-2.7.1-py3-none-any.whl.metadata (5.9 kB)
Collecting aiosignal>=1.4.0 (from aiohttp>=3.11.8->-r ComfyUI/requirements.txt (line 13))
  Downloading aiosignal-1.4.0-py3-none-any.whl.metadata (3.7 kB)
Collecting attrs>=17.3.0 (from aiohttp>=3.11.8->-r ComfyUI/requirements.txt (line 13))
  Downloading attrs-26.1.0-py3-none-any.whl.metadata (8.8 kB)
Collecting frozenlist>=1.1.1 (from aiohttp>=3.11.8->-r ComfyUI/requirements.txt (line 13))
  Downloading frozenlist-1.8.0-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (20 kB)
Collecting multidict<8.0,>=4.5 (from aiohttp>=3.11.8->-r ComfyUI/requirements.txt (line 13))
  Downloading multidict-7.2.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (6.1 kB)
Collecting propcache>=0.2.0 (from aiohttp>=3.11.8->-r ComfyUI/requirements.txt (line 13))
  Downloading propcache-0.5.4-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (25 kB)
Collecting Mako (from alembic->-r ComfyUI/requirements.txt (line 20))
  Downloading mako-1.4.3-py3-none-any.whl.metadata (2.9 kB)
Collecting charset_normalizer<4,>=2 (from requests->-r ComfyUI/requirements.txt (line 26))
  Downloading charset_normalizer-3.5.2-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (46 kB)
Collecting urllib3<3,>=1.26 (from requests->-r ComfyUI/requirements.txt (line 26))
  Downloading urllib3-2.8.0-py3-none-any.whl.metadata (7.4 kB)
Collecting certifi>=2023.5.7 (from requests->-r ComfyUI/requirements.txt (line 26))
  Downloading certifi-2026.10.23-py3-none-any.whl.metadata (2.5 kB)
Collecting kornia-rs>=0.2.0 (from kornia>=0.7.1->-r ComfyUI/requirements.txt (line 31))
  Downloading kornia_rs-0.2.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (19 kB)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in ./.venv/lib/python3.13/site-packages (from sympy>=1.13.3->torch->-r ComfyUI/requirements.txt (line 4)) (1.3.0)
Requirement already satisfied: MarkupSafe>=2.0 in ./.venv/lib/python3.13/site-packages (from jinja2->torch->-r ComfyUI/requirements.txt (line 4)) (3.0.3)
Collecting shellingham>=1.3.0 (from typer->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Downloading shellingham-1.5.4-py2.py3-none-any.whl.metadata (3.5 kB)
Collecting rich>=13.8.0 (from typer->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Downloading rich-15.0.0-py3-none-any.whl.metadata (18 kB)
Collecting annotated-doc>=0.0.2 (from typer->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Downloading annotated_doc-0.0.5-py3-none-any.whl.metadata (6.5 kB)
Collecting markdown-it-py>=2.2.0 (from rich>=13.8.0->typer->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Downloading markdown_it_py-4.2.0-py3-none-any.whl.metadata (7.4 kB)
Collecting pygments<3.0.0,>=2.13.0 (from rich>=13.8.0->typer->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Downloading pygments-2.21.0-py3-none-any.whl.metadata (2.5 kB)
Collecting mdurl~=0.1 (from markdown-it-py>=2.2.0->rich>=13.8.0->typer->transformers>=4.50.3->-r ComfyUI/requirements.txt (line 9))
  Downloading mdurl-0.1.2-py3-none-any.whl.metadata (1.6 kB)
Downloading comfyui_frontend_package-1.57.1-py3-none-any.whl (24.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 24.2/24.2 MB 53.2 MB/s  0:00:00
Downloading comfyui_workflow_templates-0.11.93-py3-none-any.whl (10 kB)
Downloading comfyui_embedded_docs-0.5.14-py3-none-any.whl (24.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 24.3/24.3 MB 142.6 MB/s  0:00:00
Downloading comfy_kitchen-0.2.39-cp312-abi3-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (65.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 65.8/65.8 MB 65.1 MB/s  0:00:01
Downloading comfy_aimdo-0.5.6-cp39-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (432 kB)
Downloading comfyui_workflow_templates_core-0.3.384-py3-none-any.whl (83 kB)
Downloading comfyui_workflow_templates_json-0.1.119-py3-none-any.whl (4.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.0/4.0 MB 135.2 MB/s  0:00:00
Downloading comfyui_workflow_templates_media_api-0.3.84-py3-none-any.whl (100.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.1/100.1 MB 39.3 MB/s  0:00:02
Downloading comfyui_workflow_templates_media_assets_01-0.1.48-py3-none-any.whl (94.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 94.2/94.2 MB 39.6 MB/s  0:00:02
Downloading comfyui_workflow_templates_media_assets_02-0.1.20-py3-none-any.whl (35.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35.1/35.1 MB 102.8 MB/s  0:00:00
Downloading comfyui_workflow_templates_media_image-0.3.160-py3-none-any.whl (89.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 89.4/89.4 MB 36.9 MB/s  0:00:02
Downloading comfyui_workflow_templates_media_other-0.3.229-py3-none-any.whl (89.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 89.1/89.1 MB 58.5 MB/s  0:00:01
Downloading comfyui_workflow_templates_media_video-0.3.101-py3-none-any.whl (104.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 104.3/104.3 MB 38.1 MB/s  0:00:02
Downloading pydantic-2.14.1-py3-none-any.whl (488 kB)
Downloading pydantic_core-2.50.1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.2/2.2 MB 123.3 MB/s  0:00:00
Downloading pydantic_settings-2.16.1-py3-none-any.whl (80 kB)
Downloading torchsde-0.2.6-py3-none-any.whl (61 kB)
Downloading einops-0.8.2-py3-none-any.whl (65 kB)
Downloading transformers-5.21.0-py3-none-any.whl (13.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 13.0/13.0 MB 206.4 MB/s  0:00:00
Downloading tokenizers-0.23.3-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (3.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.4/3.4 MB 155.2 MB/s  0:00:00
Using cached huggingface_hub-2.3.0-py3-none-any.whl (855 kB)
Using cached click-8.5.0-py3-none-any.whl (125 kB)
Using cached hf_xet-1.7.0-cp38-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (4.2 MB)
Using cached httpx2-2.16.0-py3-none-any.whl (97 kB)
Using cached httpcore2-2.16.0-py3-none-any.whl (85 kB)
Downloading sentencepiece-0.2.2-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (1.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.4/1.4 MB 115.3 MB/s  0:00:00
Downloading safetensors-0.8.0-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (516 kB)
Downloading aiohttp-3.14.5-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (1.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.9/1.9 MB 122.1 MB/s  0:00:00
Downloading yarl-1.25.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (117 kB)
Downloading multidict-7.2.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (516 kB)
Downloading pyyaml-6.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (801 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 801.6/801.6 kB 69.6 MB/s  0:00:00
Downloading scipy-1.18.1-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (35.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35.3/35.3 MB 142.9 MB/s  0:00:00
Using cached tqdm-4.70.1-py3-none-any.whl (80 kB)
Downloading psutil-7.2.2-cp36-abi3-manylinux2010_x86_64.manylinux_2_12_x86_64.manylinux_2_28_x86_64.whl (155 kB)
Downloading alembic-1.20.1-py3-none-any.whl (270 kB)
Downloading sqlalchemy-2.1.6-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (4.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.7/4.7 MB 181.5 MB/s  0:00:00
Downloading av-19.0.2-cp312-abi3-manylinux_2_28_x86_64.whl (35.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35.0/35.0 MB 65.9 MB/s  0:00:00
Downloading requests-2.34.2-py3-none-any.whl (73 kB)
Downloading charset_normalizer-3.5.2-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (254 kB)
Using cached idna-3.20-py3-none-any.whl (69 kB)
Downloading urllib3-2.8.0-py3-none-any.whl (135 kB)
Downloading simpleeval-1.0.8-py3-none-any.whl (18 kB)
Downloading blake3-1.0.11-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (381 kB)
Downloading kornia-0.9.0-py3-none-any.whl (1.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.9/1.9 MB 110.2 MB/s  0:00:00
Downloading spandrel-0.4.2-py3-none-any.whl (320 kB)
Downloading pyopengl-3.1.10-py3-none-any.whl (3.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.2/3.2 MB 182.3 MB/s  0:00:00
Downloading comfy_angle-0.1.1-py3-none-manylinux_2_28_x86_64.whl (5.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.1/5.1 MB 138.0 MB/s  0:00:00
Downloading aiohappyeyeballs-2.7.1-py3-none-any.whl (15 kB)
Downloading aiosignal-1.4.0-py3-none-any.whl (7.5 kB)
Downloading annotated_types-0.8.0-py3-none-any.whl (13 kB)
Using cached anyio-4.15.1-py3-none-any.whl (132 kB)
Downloading attrs-26.1.0-py3-none-any.whl (67 kB)
Downloading certifi-2026.10.23-py3-none-any.whl (135 kB)
Downloading frozenlist-1.8.0-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (234 kB)
Using cached h11-0.16.0-py3-none-any.whl (37 kB)
Downloading kornia_rs-0.2.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (5.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.3/5.3 MB 124.8 MB/s  0:00:00
Using cached packaging-26.3-py3-none-any.whl (129 kB)
Downloading propcache-0.5.4-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (234 kB)
Downloading python_dotenv-1.2.4-py3-none-any.whl (23 kB)
Downloading regex-2026.9.29-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (807 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 807.9/807.9 kB 77.4 MB/s  0:00:00
Downloading trampoline-0.1.2-py3-none-any.whl (5.2 kB)
Using cached truststore-0.10.5-py3-none-any.whl (19 kB)
Downloading typing_inspection-0.4.4-py3-none-any.whl (14 kB)
Downloading mako-1.4.3-py3-none-any.whl (80 kB)
Downloading typer-0.27.3-py3-none-any.whl (123 kB)
Downloading annotated_doc-0.0.5-py3-none-any.whl (5.3 kB)
Downloading rich-15.0.0-py3-none-any.whl (310 kB)
Downloading pygments-2.21.0-py3-none-any.whl (1.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 104.0 MB/s  0:00:00
Downloading markdown_it_py-4.2.0-py3-none-any.whl (91 kB)
Downloading mdurl-0.1.2-py3-none-any.whl (10.0 kB)
Downloading shellingham-1.5.4-py2.py3-none-any.whl (9.8 kB)
Installing collected packages: trampoline, PyOpenGL, urllib3, typing-inspection, truststore, tqdm, SQLAlchemy, simpleeval, shellingham, sentencepiece, scipy, safetensors, regex, pyyaml, python-dotenv, pygments, pydantic-core, psutil, propcache, packaging, multidict, mdurl, Mako, kornia-rs, idna, hf-xet, h11, frozenlist, einops, comfyui-workflow-templates-media-video, comfyui-workflow-templates-media-other, comfyui-workflow-templates-media-image, comfyui-workflow-templates-media-assets-02, comfyui-workflow-templates-media-assets-01, comfyui-workflow-templates-media-api, comfyui-workflow-templates-json, comfyui-workflow-templates-core, comfyui-frontend-package, comfyui-embedded-docs, comfy-kitchen, comfy-angle, comfy-aimdo, click, charset_normalizer, certifi, blake3, av, attrs, annotated-types, annotated-doc, aiohappyeyeballs, yarl, requests, pydantic, markdown-it-py, httpcore2, comfyui-workflow-templates, anyio, alembic, aiosignal, torchsde, rich, pydantic-settings, kornia, httpx2, aiohttp, typer, spandrel, huggingface-hub, tokenizers, transformers

Successfully installed Mako-1.4.3 PyOpenGL-3.1.10 SQLAlchemy-2.1.6 aiohappyeyeballs-2.7.1 aiohttp-3.14.5 aiosignal-1.4.0 alembic-1.20.1 annotated-doc-0.0.5 annotated-types-0.8.0 anyio-4.15.1 attrs-26.1.0 av-19.0.2 blake3-1.0.11 certifi-2026.10.23 charset_normalizer-3.5.2 click-8.5.0 comfy-aimdo-0.5.6 comfy-angle-0.1.1 comfy-kitchen-0.2.39 comfyui-embedded-docs-0.5.14 comfyui-frontend-package-1.57.1 comfyui-workflow-templates-0.11.93 comfyui-workflow-templates-core-0.3.384 comfyui-workflow-templates-json-0.1.119 comfyui-workflow-templates-media-api-0.3.84 comfyui-workflow-templates-media-assets-01-0.1.48 comfyui-workflow-templates-media-assets-02-0.1.20 comfyui-workflow-templates-media-image-0.3.160 comfyui-workflow-templates-media-other-0.3.229 comfyui-workflow-templates-media-video-0.3.101 einops-0.8.2 frozenlist-1.8.0 h11-0.16.0 hf-xet-1.7.0 httpcore2-2.16.0 httpx2-2.16.0 huggingface-hub-2.3.0 idna-3.20 kornia-0.9.0 kornia-rs-0.2.0 markdown-it-py-4.2.0 mdurl-0.1.2 multidict-7.2.1 packaging-26.3 propcache-0.5.4 psutil-7.2.2 pydantic-2.14.1 pydantic-core-2.50.1 pydantic-settings-2.16.1 pygments-2.21.0 python-dotenv-1.2.4 pyyaml-6.0.3 regex-2026.9.29 requests-2.34.2 rich-15.0.0 safetensors-0.8.0 scipy-1.18.1 sentencepiece-0.2.2 shellingham-1.5.4 simpleeval-1.0.8 spandrel-0.4.2 tokenizers-0.23.3 torchsde-0.2.6 tqdm-4.70.1 trampoline-0.1.2 transformers-5.21.0 truststore-0.10.5 typer-0.27.3 typing-inspection-0.4.4 urllib3-2.8.0 yarl-1.25.1
requirements_exit:0
=== STEP pip install shotcheck ===
Processing ./shotcheck
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Collecting comfy-sdk==0.5.0 (from shotcheck==0.1.0)
  Downloading comfy_sdk-0.5.0-py3-none-any.whl.metadata (62 kB)
Collecting comfy-api-proxy==0.1.6 (from shotcheck==0.1.0)
  Downloading comfy_api_proxy-0.1.6-py3-none-any.whl.metadata (17 kB)
Collecting opencv-python==5.0.0.93 (from shotcheck==0.1.0)
  Downloading opencv_python-5.0.0.93-cp37-abi3-manylinux_2_28_x86_64.whl.metadata (19 kB)
Requirement already satisfied: numpy<3,>=2 in ./.venv/lib/python3.13/site-packages (from shotcheck==0.1.0) (2.5.2)
Requirement already satisfied: torch>=2.10 in ./.venv/lib/python3.13/site-packages (from shotcheck==0.1.0) (2.14.1+cpu)
Requirement already satisfied: aiohttp>=3.9 in ./.venv/lib/python3.13/site-packages (from comfy-api-proxy==0.1.6->shotcheck==0.1.0) (3.14.5)
Requirement already satisfied: blake3>=0.4 in ./.venv/lib/python3.13/site-packages (from comfy-api-proxy==0.1.6->shotcheck==0.1.0) (1.0.11)
Requirement already satisfied: pydantic>=2.6 in ./.venv/lib/python3.13/site-packages (from comfy-api-proxy==0.1.6->shotcheck==0.1.0) (2.14.1)
Requirement already satisfied: pyyaml>=6.0 in ./.venv/lib/python3.13/site-packages (from comfy-api-proxy==0.1.6->shotcheck==0.1.0) (6.0.3)
Collecting httpx>=0.27 (from comfy-sdk==0.5.0->shotcheck==0.1.0)
  Downloading httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
Requirement already satisfied: aiohappyeyeballs>=2.5.0 in ./.venv/lib/python3.13/site-packages (from aiohttp>=3.9->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (2.7.1)
Requirement already satisfied: aiosignal>=1.4.0 in ./.venv/lib/python3.13/site-packages (from aiohttp>=3.9->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (1.4.0)
Requirement already satisfied: attrs>=17.3.0 in ./.venv/lib/python3.13/site-packages (from aiohttp>=3.9->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (26.1.0)
Requirement already satisfied: frozenlist>=1.1.1 in ./.venv/lib/python3.13/site-packages (from aiohttp>=3.9->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (1.8.0)
Requirement already satisfied: multidict<8.0,>=4.5 in ./.venv/lib/python3.13/site-packages (from aiohttp>=3.9->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (7.2.1)
Requirement already satisfied: propcache>=0.2.0 in ./.venv/lib/python3.13/site-packages (from aiohttp>=3.9->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (0.5.4)
Requirement already satisfied: yarl<2.0,>=1.25.1 in ./.venv/lib/python3.13/site-packages (from aiohttp>=3.9->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (1.25.1)
Requirement already satisfied: idna>=2.0 in ./.venv/lib/python3.13/site-packages (from yarl<2.0,>=1.25.1->aiohttp>=3.9->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (3.20)
Requirement already satisfied: anyio in ./.venv/lib/python3.13/site-packages (from httpx>=0.27->comfy-sdk==0.5.0->shotcheck==0.1.0) (4.15.1)
Requirement already satisfied: certifi in ./.venv/lib/python3.13/site-packages (from httpx>=0.27->comfy-sdk==0.5.0->shotcheck==0.1.0) (2026.10.23)
Collecting httpcore==1.* (from httpx>=0.27->comfy-sdk==0.5.0->shotcheck==0.1.0)
  Downloading httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
Requirement already satisfied: h11>=0.16 in ./.venv/lib/python3.13/site-packages (from httpcore==1.*->httpx>=0.27->comfy-sdk==0.5.0->shotcheck==0.1.0) (0.16.0)
Requirement already satisfied: annotated-types>=0.6.0 in ./.venv/lib/python3.13/site-packages (from pydantic>=2.6->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (0.8.0)
Requirement already satisfied: pydantic-core==2.50.1 in ./.venv/lib/python3.13/site-packages (from pydantic>=2.6->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (2.50.1)
Requirement already satisfied: typing-extensions>=4.16.0 in ./.venv/lib/python3.13/site-packages (from pydantic>=2.6->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (4.16.0)
Requirement already satisfied: typing-inspection>=0.4.4 in ./.venv/lib/python3.13/site-packages (from pydantic>=2.6->comfy-api-proxy==0.1.6->shotcheck==0.1.0) (0.4.4)
Requirement already satisfied: filelock in ./.venv/lib/python3.13/site-packages (from torch>=2.10->shotcheck==0.1.0) (3.32.3)
Requirement already satisfied: setuptools>=77.0.3 in ./.venv/lib/python3.13/site-packages (from torch>=2.10->shotcheck==0.1.0) (78.1.0)
Requirement already satisfied: sympy>=1.13.3 in ./.venv/lib/python3.13/site-packages (from torch>=2.10->shotcheck==0.1.0) (1.14.0)
Requirement already satisfied: networkx>=2.5.1 in ./.venv/lib/python3.13/site-packages (from torch>=2.10->shotcheck==0.1.0) (3.6.1)
Requirement already satisfied: jinja2 in ./.venv/lib/python3.13/site-packages (from torch>=2.10->shotcheck==0.1.0) (3.1.6)
Requirement already satisfied: fsspec>=0.8.5 in ./.venv/lib/python3.13/site-packages (from torch>=2.10->shotcheck==0.1.0) (2026.7.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in ./.venv/lib/python3.13/site-packages (from sympy>=1.13.3->torch>=2.10->shotcheck==0.1.0) (1.3.0)
Requirement already satisfied: MarkupSafe>=2.0 in ./.venv/lib/python3.13/site-packages (from jinja2->torch>=2.10->shotcheck==0.1.0) (3.0.3)
Downloading comfy_api_proxy-0.1.6-py3-none-any.whl (59 kB)
Downloading comfy_sdk-0.5.0-py3-none-any.whl (165 kB)
Downloading opencv_python-5.0.0.93-cp37-abi3-manylinux_2_28_x86_64.whl (73.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 73.8/73.8 MB 59.5 MB/s  0:00:01
Downloading httpx-0.28.1-py3-none-any.whl (73 kB)
Downloading httpcore-1.0.9-py3-none-any.whl (78 kB)
Building wheels for collected packages: shotcheck
  Building wheel for shotcheck (pyproject.toml): started
  Building wheel for shotcheck (pyproject.toml): finished with status 'done'
  Created wheel for shotcheck: filename=shotcheck-0.1.0-py3-none-any.whl size=25166 sha256=3fa21ad85fe4804b9c2ff5900d540baadb59215363cc65af849faf1b28738faa
  Stored in directory: /tmp/pip-ephem-wheel-cache-qg5ksk49/wheels/fd/2b/90/669732c1908a414f3b40023aea01799c4667bc58566ea203b7
Successfully built shotcheck
Installing collected packages: opencv-python, httpcore, httpx, comfy-sdk, comfy-api-proxy, shotcheck

Successfully installed comfy-api-proxy-0.1.6 comfy-sdk-0.5.0 httpcore-1.0.9 httpx-0.28.1 opencv-python-5.0.0.93 shotcheck-0.1.0
shotcheck_exit:0
=== STEP copy node ===
copy_exit:0
=== STEP app ===
page_try_1:000
page_try_2:000
page_try_3:000
page_try_4:000
page_try_5:000
page_try_6:000
page_try_7:000
page_try_8:000
page_try_9:000
page_try_10:000
=== STEP analysis ===
check_http:000
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
FileNotFoundError: [Errno 2] No such file or directory: 'check.json'
=== DONE ===
```
