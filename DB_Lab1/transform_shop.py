from lxml import etree

def transform_shop():
    tree = etree.parse("petmarket.xml")
    xslt_root = etree.XML('''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <xsl:template match="/">
            <html xmlns="http://www.w3.org/1999/xhtml">
                <table border="1">
                    <xsl:for-each select="data/product">
                        <tr bgcolor="#F5F5F5">
                            <td>
                                <img>
                                    <xsl:attribute name="src">
                                        <xsl:value-of select="image"/>
                                    </xsl:attribute>
                                </img>
                            </td>
                            <td align="left">
                                <strong>
                                    <xsl:value-of select="name"/>
                                </strong>
                            </td>
                            <td>
                                <xsl:value-of select="price"/>
                            </td>
                        </tr>
                    </xsl:for-each>
                </table>
            </html>
        </xsl:template>
    </xsl:stylesheet>''')

    transform = etree.XSLT(xslt_root)

    my_file = open("petmarket-t.xhtml", 'wb')
    my_file.write(etree.tostring(transform(tree)))
    my_file.close()