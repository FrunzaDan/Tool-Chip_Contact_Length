# Known Gaps

Things known to be incomplete, fragile, or empirically-hacky, kept here so future work has a starting list instead of rediscovering them by reading code.

## Contact-length annotation text has a stray literal

`src/getHoughLines.py`, `save_result_image` — the annotation text is built as `f"Dist = {contact_length}px + t"`. The trailing `+ t` is not a variable, it's literal text baked into the f-string, so every result image is annotated e.g. `Dist = 42px + t` instead of `Dist = 42px`. Looks like a leftover debug artifact rather than intended output.

## Vertical-line position thresholds are dimensionally inconsistent

`src/getHoughLines.py`, `get_vertical_line_Y_index` — `threshold_a` (half the image *height*) is compared against x-coordinates, and `threshold_b` (half the *width*) is compared against a mix of `y1` and `x2` (not a consistent `y1`/`y2` pair). The in-code comment says this was tested deliberately: swapping to the dimensionally "correct" pairing rejects the real tool edge and regresses detection on the actual dataset. It works, but the geometric criterion it's actually encoding has never been re-derived — worth revisiting with a principled position filter (e.g. bounding-box based) rather than reusing a magic pair of `shape[0]/2`, `shape[1]/2` thresholds. See [[line_detection_and_measurement]].

## No automated tests

No `tests/` directory or test framework anywhere in the repo. There's no way to catch a pipeline regression (e.g. from a parameter change, see [[pipeline_parameters]]) other than eyeballing the diagnostic plots in `Output/folder_plot_results/` for a full dataset run.

## Pipeline parameters are tuned to one dataset/camera setup

Every threshold in [[pipeline_parameters]] (resize width, OTSU range, morphology kernels, Hough thresholds, angle/position tolerances) was tuned against the single dataset in `Input/Complete_Dataset/`. Nothing is measured or derived from the image itself (e.g. relative to detected object size), so a different camera, lens, or lighting setup would likely require re-tuning most of these by hand, with no documented process for how the current values were chosen.

## No sanity check on the computed contact length

`contact_length = y_point_of_horizontal - y_point_of_vertical` (`src/getHoughLines.py`) is written straight to the output image with no bounds/sign check. If line classification picks the "wrong" horizontal/vertical line on a noisy frame, a negative or implausibly large value is saved and looks like a normal result — there's no automatic way to flag it as suspect during a batch run.

## `get_contours` degrades to a 1x1 stub image on bad input

`src/getContours.py`, `get_contours` — if `dilation_img is None`, it returns `np.zeros((1, 1, 3))`. That 1x1 image is then passed into `getHoughLines.get_hough_lines_function` as if it were a normal frame; nothing downstream expects a 1x1 image, so this path is untested and more likely to raise deeper in the pipeline than to fail at a clear, well-logged point.

## `.env` support is wired but unused

`.vscode/launch.json` declares `"envFile": "${workspaceFolder}/.env"`, but no `.env` (or `.env.example`) file exists and no source file reads `os.environ`. Either remove the hook or document what it's meant to configure once something actually needs it.

## No CLI arguments or config file

Input/output folder paths (`Input/Complete_Dataset/`, `Output/folder_hough_results/`, `Output/folder_plot_results/`) are hardcoded relative to `src/` in `folderLoop.py`. Running against a different dataset means either replacing the contents of `Input/Complete_Dataset/` or editing source — there's no `--input`/`--output` flag or config file.

## `ai_docs/` scaffold is partially set up

`ai_docs/learning_approach.md` describes a workflow that also expects `todo.md` and `glossary.md` to track documented-vs-pending concepts and terminology — neither file exists yet, so that part of the protocol isn't actually followable yet.
