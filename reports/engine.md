# Engine Identification

Workspace: `C:\Users\rahma\Documents\projects\abe\reverse_engineering`

## Conclusion

The game is most likely built with Unreal Engine 4.

Confidence: HIGH

## Evidence

| Evidence | Source | Confidence |
|---|---|---|
| APK contains `lib/arm64-v8a/libUE4.so` and `lib/armeabi-v7a/libUE4.so`. | `PES-CLUB-MANAGER-v4-5-1.apk` ZIP listing | HIGH |
| APK native library entry `lib/arm64-v8a/libUE4.so` is 126,185,464 bytes; SHA-256 `736f2d7e2d0ed4e866a65602c66a5d0f2ef93701fd08c9c79d75b18ad9b6d275`. | APK ZIP stream metadata and entry hash | HIGH |
| APK native library entry `lib/armeabi-v7a/libUE4.so` is 104,135,952 bytes; SHA-256 `19501074b9e8023aead92392894c78dce56b65ae68582dc523fa633dd2df57a2`. | APK ZIP stream metadata and entry hash | HIGH |
| Main OBB contains `PesMobile/Content/Paks/PesMobile-Android_ETC1.pak`. | `jp.konami.pesclubmanager/main.104050101.jp.konami.pesclubmanager.obb` ZIP listing | HIGH |
| The `.pak` path follows the common Unreal layout `ProjectName/Content/Paks/*.pak`. | `PesMobile/Content/Paks/PesMobile-Android_ETC1.pak` | HIGH |

## Negative Checks

| Engine indicator | Result | Confidence |
|---|---|---|
| Unity native runtime: `libunity.so` | Not present in APK listing checked during this pass. | MEDIUM |
| Unity IL2CPP runtime: `libil2cpp.so` | Not present in APK listing checked during this pass. | MEDIUM |
| Unity metadata: `global-metadata.dat` | Not present in APK listing checked during this pass. | MEDIUM |
| Unity/Mono managed code: `Assembly-CSharp.dll` | Not present in APK listing checked during this pass. | MEDIUM |

## Related Containers

| Artifact | Observed format | Purpose hypothesis | Confidence |
|---|---|---|---|
| `main.104050101.jp.konami.pesclubmanager.obb` | ZIP-style OBB, starts with `50 4B 03 04`. | Expansion file containing Unreal package assets. | HIGH |
| `patch.104050101.jp.konami.pesclubmanager.obb` | Starts with ASCII `CPK`; Java ZIP listing fails. | Likely CRI CPK or CPK-like patch asset container. | HIGH |

## IL2CPP / Mono Assessment

No IL2CPP or Mono evidence was found in the static archive listing. The native runtime evidence points to Unreal Engine, not Unity.

Confidence: HIGH for "not Unity"; MEDIUM for "no managed gameplay assembly" until APK decompilation is completed.

## Unity Version

Not applicable based on current evidence.

## Unreal Version

Unknown at this stage.

Next experiment:

1. Extract `libUE4.so` into `extracted/apk/` during APK analysis.
2. Run static string/symbol checks against `libUE4.so`.
3. Inspect package metadata and Unreal strings for build/version markers.
4. Inspect `PesMobile-Android_ETC1.pak` header and mount metadata using safe read-only tooling.

## Unknowns

| Unknown | Next experiment |
|---|---|
| Exact Unreal Engine version | Search `libUE4.so` strings and `.pak` metadata after extraction. |
| Whether the `.pak` is encrypted, compressed, signed, or custom-mounted | Inspect `.pak` header and Unreal pak index behavior. |
| Meaning and format of the patch OBB `CPK` container | Identify CPK table/header structure and list contents with read-only parser/tool. |
