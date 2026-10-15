# Third-party notices

Super Punch-Out!! for PC (TanookiStudios/SuperPunchOutRecomp) is built on the components below. Their license texts follow.

This is a fan-made program. It contains no game data: you supply your own Super Punch-Out!! (USA) ROM.

## snesrecomp, by Matthew Stanley (PolyForm Noncommercial License 1.0.0)

The engine (SNES hardware model, desktop host, and launcher plumbing). Source: https://github.com/mstan/snesrecomp

```
PolyForm Noncommercial License 1.0.0

<https://polyformproject.org/licenses/noncommercial/1.0.0>

Copyright (c) 2026 Matthew Stanley

## Acceptance

In order to get any license under these terms, you must agree to them as
both strict obligations and conditions to all your licenses.

## Copyright License

The licensor grants you a copyright license for the software to do
everything you might otherwise need the licensor's permission to do. Your
license covers distributing the software, making changes and new works
based on it, and all other uses of the software, subject to the
limitations and conditions in these terms.

## Noncommercial Purposes

Any noncommercial purpose is a permitted purpose.

## Personal Uses

Personal use for research, experiment, and testing for the benefit of
public knowledge, personal study, private entertainment, hobby projects,
amateur pursuits, or religious observance, without any anticipated
commercial application, counts as use for a permitted purpose.

## Noncommercial Organizations

Use by any charitable organization, educational institution, public
research organization, public safety or health organization, environmental
protection organization, or government institution counts as use for a
permitted purpose regardless of the source of funding or obligations
resulting from the funding.

## Fair Use

You may have "fair use" rights for the software under the law. These
terms do not limit them.

## No Other Rights

These terms do not allow you to sublicense or transfer any of your
licenses to anyone else, or prevent the licensor from granting licenses to
anyone else. These terms do not imply any other licenses.

## Patent Defense

If you make any written claim that the software infringes or contributes
to infringement of any patent, your patent license for the software granted
under these terms ends immediately. If your company makes such a claim,
your patent license ends immediately for work on behalf of your company.

## Violations

The first time you are notified in writing that you have violated any of
these terms, or done anything with the software not covered by your
licenses, your licenses can nonetheless continue if you come into full
compliance with these terms, and take practical steps to correct past
violations, within 32 days of receiving notice. Otherwise, all your
licenses end immediately.

## No Liability

As far as the law allows, the software comes as is, without any warranty
or condition, and the licensor will not be liable to you for any damages
arising out of these terms or the use or nature of the software, under any
kind of legal claim.

## Definitions

The **licensor** is the individual or entity offering these terms, and the
**software** is the software the licensor makes available under these
terms.

**You** refers to the individual or entity agreeing to these terms.

**Your company** is any legal entity, sole proprietorship, or other kind
of organization that you work for, plus all organizations that have control
over, are under the control of, or are under common control with that
organization. **Control** means ownership of substantially all the assets
of an entity, or the power to direct its management and policies by vote,
contract, or otherwise. Control can be direct or indirect.

**Your licenses** are all the licenses granted to you for the software
under these terms.

**Use** means anything you do with the software requiring one of your
licenses.

---

For the avoidance of doubt, the licensor's intent is to restrict uses where
profit is derived from this software. Non-profit personal, educational,
or community use is welcome regardless of organizational context.

For commercial licensing inquiries, contact the licensor, Matthew Stanley,
at <https://1379.tech>.
```

## recomp-ui (MIT)

```
MIT License

Copyright (c) 2026 Matthew Stanley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Dear ImGui (MIT)

```
The MIT License (MIT)

Copyright (c) 2014-2025 Omar Cornut

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## SDL3 3.4.10 (zlib)

Built from source and linked into the program.

```
Copyright (C) 1997-2026 Sam Lantinga <slouken@libsdl.org>
  
This software is provided 'as-is', without any express or implied
warranty.  In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:
  
1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required. 
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.
```

## SDL_GameControllerDB (zlib), assets/gamecontrollerdb.txt

```
Copyright (C) 1997-2025 Sam Lantinga <slouken@libsdl.org>
  
This software is provided 'as-is', without any express or implied
warranty.  In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:
  
1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required. 
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.
```

## Code inside the snesrecomp engine (linked into the program)

snesrecomp itself contains the third-party code below; its license notices must
travel with the program, so they are reproduced here. Details and provenance:
vendor/snesrecomp/THIRD_PARTY_ATTRIBUTION.md in the snesrecomp source.

### snesrev (zelda3 / smw): the C SNES hardware core and runtime utilities (MIT)

https://github.com/snesrev/zelda3 and https://github.com/snesrev/smw

```
Copyright (c) 2022 snesrev
Copyright (c) 2023 snesrev
Copyright (c) 2021 elzo_d

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### LakeSnes by angelo_wf: the 65816 interpreter core (MIT)

https://github.com/angelo-wf/lakesnes

```
Copyright (c) 2021-2023 angelo_wf and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### ares: Cx4, DSP-1 and SA-1 coprocessor cores (ISC)

https://github.com/ares-emulator/ares

```
ares

Copyright (c) 2004-2025 ares team, Near et al

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

### S-DD1 decompression (public domain)

Andreas Naive's S-DD1 algorithm code (via bsnes-plus), which states: "This code is Public Domain. There is no copyright holded by the author." Credit is kept as a courtesy.

### Screen-color model (MIT)

The screen-color tables derive from JRickey/gba-recomp (MIT OR Apache-2.0, used here under MIT) via mstan/psxrecomp.

```
MIT License

Copyright (c) 2022 Jrickey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### OpenGL loader and image loader

The OpenGL 3.1 core loader is generated output of glLoadGen (Jason McKesson), which places no restriction on its output. stb_image (Sean Barrett) is public domain or MIT, at your option.

## Launcher fonts and images (shipped in assets/)

### Font licenses

#### OpenMoji (`OpenMoji-black-glyf.ttf`)

Copyright © OpenMoji Project  
License: [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)

Used as an emoji fallback (e.g. kick 🥾) merged into the launcher UI font.

#### Noto Sans Symbols 2 (`NotoSansSymbols2-Regular.ttf`)

Copyright © The Noto Project Authors  
License: [SIL Open Font License 1.1 (OFL-1.1)](https://scripts.sil.org/OFL)

Used as a symbols fallback merged into the launcher UI font.

#### LatoLatin (`LatoLatin-Regular.ttf`, `LatoLatin-Bold.ttf`)

Copyright (c) 2010-2015, Łukasz Dziedzic (dziedzic@typoland.com), with Reserved Font Name "Lato".
License: [SIL Open Font License 1.1 (OFL-1.1)](https://scripts.sil.org/OFL)

These Regular and Bold files are the Lato 2.015 Latin subset. Their contents match the corresponding `lato-regular.ttf` and `lato-bold.ttf` files in the [LatoLatin Webfont package](https://github.com/hakger/latolatin-webfont/tree/4a7162e18a6a01f2ce87dec05c4e4605d8167eb6); its [README](https://github.com/hakger/latolatin-webfont/blob/4a7162e18a6a01f2ce87dec05c4e4605d8167eb6/README.md) documents the subset provenance, and its [OFL.txt](https://github.com/hakger/latolatin-webfont/blob/4a7162e18a6a01f2ce87dec05c4e4605d8167eb6/OFL.txt) carries the license.

### Image licenses

#### Country flags (`flags.png`)

Rendered from Noto Color Emoji, Copyright © The Noto Project Authors  
License: [SIL Open Font License 1.1 (OFL-1.1)](https://scripts.sil.org/OFL)

A 26x26 sprite sheet of every flag the font ships, indexed by region code
(row = first letter, column = second). Regenerate with
`tools/gen_flag_sheet.py`. Bundled because Windows' Segoe UI Emoji has no
flag glyphs, and so that a country reads the same on every platform.

## Other bundled libraries

- stb_image, stb_image_write, stb_truetype (Sean Barrett): public domain or MIT, at your option.
- tinyfiledialogs (Guillaume Vareille): zlib license.
- The app icon and Maddie's signature are original artwork by Tanooki Studios.
