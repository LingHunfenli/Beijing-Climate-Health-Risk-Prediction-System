"""
将所有图片从内嵌型改为上下型环绕（wrapTopAndBottom）
"""
import os
from docx import Document
from docx.oxml.ns import qn, nsmap
from lxml import etree

DOC_PATH = "北京市气候健康风险预警—智能体可视化平台_毕业论文.docx"
doc = Document(DOC_PATH)

# XML namespaces
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PIC = 'http://schemas.openxmlformats.org/drawingml/2006/picture'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

ns = {
    'wp': WP,
    'a': A,
    'pic': PIC,
    'r': R,
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
}

count = 0
for para in doc.paragraphs:
    for run in para.runs:
        drawings = run._element.findall('.//' + qn('wp:inline'))
        for inline in drawings:
            # Get the parent run element
            parent = inline.getparent()

            # Extract key info from inline
            extent = inline.find(qn('wp:extent'))
            effectExtent = inline.find(qn('wp:effectExtent'))
            docPr = inline.find(qn('wp:docPr'))
            graphic = inline.find(qn('a:graphic'))

            if extent is None or docPr is None or graphic is None:
                continue

            cx = extent.get('cx', '0')
            cy = extent.get('cy', '0')
            name = docPr.get('name', '')
            descr = docPr.get('descr', '')
            docPr_id = docPr.get('id', '1')

            # Create wp:anchor element
            anchor = etree.SubElement(parent, qn('wp:anchor'), nsmap={
                'wp': WP,
                'a': A,
                'pic': PIC,
                'r': R,
            })

            # Copy attributes
            anchor.set('simplePos', '0')
            anchor.set('relativeHeight', '0')
            anchor.set('behindDoc', '0')
            anchor.set('locked', '0')
            anchor.set('layoutInCell', '1')
            anchor.set('allowOverlap', '1')

            # Add simplePos (required even though simplePos="0")
            simplePos = etree.SubElement(anchor, qn('wp:simplePos'))
            simplePos.set('x', '0')
            simplePos.set('y', '0')

            # Position horizontally: centered relative to page
            positionH = etree.SubElement(anchor, qn('wp:positionH'))
            positionH.set('relativeFrom', 'page')
            posOffsetH = etree.SubElement(positionH, qn('wp:posOffset'))
            posOffsetH.text = '0'
            # Use align center instead of fixed offset for proper centering
            positionH.remove(posOffsetH)
            alignH = etree.SubElement(positionH, qn('wp:align'))
            alignH.text = 'center'

            # Position vertically: below previous paragraph
            positionV = etree.SubElement(anchor, qn('wp:positionV'))
            positionV.set('relativeFrom', 'paragraph')
            posOffsetV = etree.SubElement(positionV, qn('wp:posOffset'))
            posOffsetV.text = '0'

            # Copy extent
            newExtent = etree.SubElement(anchor, qn('wp:extent'))
            newExtent.set('cx', cx)
            newExtent.set('cy', cy)

            # Copy effectExtent if present
            if effectExtent is not None:
                newEffect = etree.SubElement(anchor, qn('wp:effectExtent'))
                newEffect.set('l', effectExtent.get('l', '0'))
                newEffect.set('t', effectExtent.get('t', '0'))
                newEffect.set('r', effectExtent.get('r', '0'))
                newEffect.set('b', effectExtent.get('b', '0'))

            # Top and bottom wrapping
            wrap = etree.SubElement(anchor, qn('wp:wrapTopAndBottom'))

            # Copy docPr
            newDocPr = etree.SubElement(anchor, qn('wp:docPr'))
            newDocPr.set('id', docPr_id)
            newDocPr.set('name', name)
            if descr:
                newDocPr.set('descr', descr)

            # Copy graphic element (deep copy to preserve all children)
            anchor.append(etree.fromstring(etree.tostring(graphic)))

            # Remove the old inline element
            parent.remove(inline)

            count += 1
            print(f"  [{count}] Converted: {name[:50]}")

doc.save(DOC_PATH)
print(f"\nDone! {count} images converted to 上下型环绕 (wrapTopAndBottom).")
print(f"File: {DOC_PATH} ({os.path.getsize(DOC_PATH)/1024:.0f} KB)")
