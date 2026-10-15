// make_icon.swift - draws the app icon: original pixel art (a red boxing glove in
// front of a boxing ring), no artwork from the game.
//
//   swift tools/make_icon.swift <out.png> <size> [--full]
//
// Default: macOS icon layout (artwork inset in a rounded square, transparent
// margin). --full: artwork fills the square (Windows .ico).
import AppKit

let args = CommandLine.arguments
let outPath = args[1]
let size = Int(args[2])!
let full = args.contains("--full")

func rgb(_ hex: UInt32) -> NSColor {
    NSColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255,
            blue: CGFloat(hex & 255) / 255, alpha: 1)
}

// 32 x 32 grid. Back to front: dark crowd, ring ropes, blue canvas, then the glove.
var grid = [[UInt32?]](repeating: [UInt32?](repeating: nil, count: 32), count: 32)
func fillRows(_ a: Int, _ b: Int, _ color: UInt32) { for r in a...b { for c in 0..<32 { grid[r][c] = color } } }

// Crowd (rows 0-8): near-black, with a few lit faces and shirts in the dark.
fillRows(0, 8, 0x16122C)
fillRows(5, 8, 0x1F1A3C)
let crowdColors: [UInt32] = [0x6A4A5E, 0x3E4C86, 0x7A5A48, 0x4C3E7A, 0x8A4A58]
var seed = 7
for (i, c) in stride(from: 1, to: 31, by: 3).enumerated() {
    seed = (seed * 31 + 11) % 97
    let row = 3 + (seed % 3)
    let color = crowdColors[(i + seed) % crowdColors.count]
    for (dr, dc) in [(0, 0), (0, 1), (1, 0), (1, 1)] { grid[row + dr][c + dc] = color }
}
// Spotlight glow across the top.
for c in 0..<32 { grid[0][c] = (c / 4) % 2 == 0 ? 0x2A2450 : 0x1E1A3E }

// Ring backdrop between and behind the ropes (rows 9-21).
fillRows(9, 21, 0x2B2150)
// Ropes: red, white, red, each 2 rows with a highlight row on top and a shadow below.
func rope(_ r: Int, _ light: UInt32, _ mid: UInt32, _ dark: UInt32) {
    for c in 0..<32 { grid[r][c] = light; grid[r + 1][c] = mid; grid[r + 2][c] = dark }
}
rope(9, 0xFF8A7A, 0xE02A28, 0x8E1418)
rope(14, 0xFFFFFF, 0xE8E8F0, 0x9AA0B8)
rope(19, 0xFF8A7A, 0xE02A28, 0x8E1418)

// Canvas (rows 22-31): blue mat with a lighter edge and darker floor.
fillRows(22, 31, 0x2C60CC)
for c in 0..<32 { grid[22][c] = 0x7AA8F4; grid[23][c] = 0x4A82E0 }
fillRows(28, 31, 0x2450AC)
for c in stride(from: 0, to: 32, by: 8) { for r in 24...31 { grid[r][c] = 0x2450AC } }

// The glove: built from three shapes (fist, thumb, cuff), outlined and shaded in code.
// Coordinates are (column, row) in grid cells, measured at the cell centers.
func inEllipse(_ x: Double, _ y: Double, _ cx: Double, _ cy: Double, _ rx: Double, _ ry: Double) -> Bool {
    let dx = (x - cx) / rx, dy = (y - cy) / ry
    return dx * dx + dy * dy <= 1
}
func inRoundRect(_ x: Double, _ y: Double, _ x0: Double, _ y0: Double, _ x1: Double, _ y1: Double, _ r: Double) -> Bool {
    if x < x0 || x > x1 || y < y0 || y > y1 { return false }
    let cx = min(max(x, x0 + r), x1 - r), cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r
}
// Part ids: 0 none, 1 fist, 2 thumb, 3 cuff.
func part(_ c: Int, _ r: Int) -> Int {
    let x = Double(c) + 0.5, y = Double(r) + 0.5
    if inRoundRect(x, y, 11, 21, 24, 29, 1.0) { return 3 }
    if inEllipse(x, y, 9.5, 15, 4.6, 5.4) { return 2 }
    if inEllipse(x, y, 17.5, 10.75, 8.8, 8.2) { return 1 }
    if inRoundRect(x, y, 13, 14, 22, 21.5, 2) { return 1 }   // wrist, joins fist to cuff
    return 0
}
let ink: UInt32 = 0x2A0A10
let redLight: UInt32 = 0xFF6A58, red: UInt32 = 0xDC2424, redShade: UInt32 = 0x9C1620, crease: UInt32 = 0x5E0A14
let white: UInt32 = 0xF6F6FA, whiteShade: UInt32 = 0xB4B8CC, band: UInt32 = 0xDC2424

var parts = [[Int]](repeating: [Int](repeating: 0, count: 32), count: 32)
for r in 0..<32 { for c in 0..<32 { parts[r][c] = part(c, r) } }
func at(_ c: Int, _ r: Int) -> Int { (0..<32).contains(c) && (0..<32).contains(r) ? parts[r][c] : 0 }

for r in 0..<32 {
    for c in 0..<32 {
        let p = parts[r][c]
        if p == 0 { continue }
        let nbrs = [at(c - 1, r), at(c + 1, r), at(c, r - 1), at(c, r + 1)]
        // Outside edge of the whole glove: ink outline.
        if nbrs.contains(0) { grid[r][c] = ink; continue }
        // Thumb drawn in front of fist and cuff: crease line along its edge.
        if p == 2 && nbrs.contains(where: { $0 != 2 }) { grid[r][c] = crease; continue }
        // Fist next to the cuff: seam.
        if p == 1 && nbrs.contains(3) { grid[r][c] = crease; continue }
        let x = Double(c) + 0.5, y = Double(r) + 0.5
        switch p {
        case 1:
            let nx = (x - 17.5) / 8.8, ny = (y - 10.75) / 8.2
            let light = -(nx * 0.7 + ny * 0.7)
            grid[r][c] = light > 0.62 ? redLight : (light < -0.55 ? redShade : red)
        case 2:
            let nx = (x - 9.5) / 4.6, ny = (y - 15) / 5.4
            let light = -(nx * 0.7 + ny * 0.7)
            grid[r][c] = light > 0.45 ? redLight : (light < -0.3 ? redShade : red)
        default:
            // Cuff: white with a red band across the top and a shaded right side.
            if r == 24 || r == 25 { grid[r][c] = c >= 22 ? redShade : band }
            else if c >= 22 { grid[r][c] = whiteShade }
            else { grid[r][c] = white }
        }
    }
}
// A highlight spot on the fist and thumb.
for (c, r) in [(13, 4), (14, 4), (12, 5), (13, 5), (12, 6), (6, 12), (7, 11), (7, 12)] where parts[r][c] == 1 { grid[r][c] = 0xFFC8BC }

// Render: whole pixels only, so the art stays crisp.
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: size, pixelsHigh: size, bitsPerSample: 8,
                           samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
                           bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
let ctx = NSGraphicsContext(bitmapImageRep: rep)!
NSGraphicsContext.current = ctx
ctx.imageInterpolation = .none
ctx.shouldAntialias = false

let art = full ? CGFloat(size) : CGFloat(size) * 832 / 1024   // Apple's grid: 824-ish content in 1024
let cell = art / 32
let origin = (CGFloat(size) - art) / 2
let radius = art * (full ? 0.18 : 0.225)
let frame = NSRect(x: origin, y: origin, width: art, height: art)
ctx.shouldAntialias = true
NSBezierPath(roundedRect: frame, xRadius: radius, yRadius: radius).addClip()
ctx.shouldAntialias = false
for r in 0..<32 {
    for c in 0..<32 {
        guard let color = grid[r][c] else { continue }
        rgb(color).setFill()
        // AppKit's y axis points up; row 0 is the top.
        let x = (origin + CGFloat(c) * cell).rounded(.down)
        let y = (origin + art - CGFloat(r + 1) * cell).rounded(.down)
        let x2 = (origin + CGFloat(c + 1) * cell).rounded(.down)
        let y2 = (origin + art - CGFloat(r) * cell).rounded(.down)
        NSRect(x: x, y: y, width: x2 - x, height: y2 - y).fill()
    }
}
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: outPath))
