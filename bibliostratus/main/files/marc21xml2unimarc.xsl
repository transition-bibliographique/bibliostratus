<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:marc="http://www.loc.gov/MARC21/slim" version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" exclude-result-prefixes="marc">
	<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
	<xsl:template match="/">
		<collection>
			<xsl:for-each select="marc:collection">
				<xsl:for-each select="marc:record">
					<record xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
						xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/ standards/marcxml/schema/MARC21slim.xsd"
						xmlns="http://www.loc.gov/MARC21/slim">
						<xsl:variable name="leader" select="leader"/>
						<leader>
							<!-- A calculer, mais comment ? -->
							<xsl:variable name="len">00000</xsl:variable>
							<xsl:variable name="stat">
								<xsl:choose>
									<xsl:when test="substring(leader, 6, 1) = 'a'">p</xsl:when>
									<xsl:otherwise>
										<xsl:value-of select="substring(leader, 6, 1)"/>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:variable>
							<xsl:variable name="type">
								<xsl:choose>
									<xsl:when test="substring(leader, 7, 1) = 'o'">m</xsl:when>
									<xsl:when test="substring(leader, 7, 1) = 'r'">n</xsl:when>
									<xsl:otherwise>
										<xsl:value-of select="substring(leader, 7, 1)"/>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:variable>
							<xsl:variable name="biblvl">
								<xsl:choose>
									<xsl:when test="substring(leader, 8, 1) = 'b'">m</xsl:when>
									<xsl:when test="substring(leader, 8, 1) = 'd'">m</xsl:when>
									<xsl:otherwise>
										<xsl:value-of select="substring(leader, 8, 1)"/>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:variable>
							<!-- A calculer, mais comment ? -->
							<xsl:variable name="baod">02200</xsl:variable>
							<xsl:variable name="enclvl">
								<xsl:choose>
									<xsl:when test="substring(leader, 18, 1) = '8'">2</xsl:when>
									<xsl:when test="substring(leader, 17, 1) = '5'">3</xsl:when>
									<xsl:when test="substring(leader, 18, 1) = '7'">3</xsl:when>
									<xsl:otherwise>
										<xsl:value-of select="substring(leader, 18, 1)"/>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:variable>
							<xsl:variable name="dcf">
								<xsl:choose>
									<xsl:when test="substring(leader, 19, 1) = ' '">n</xsl:when>
									<xsl:otherwise>
										<xsl:value-of select="' '"/>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:variable>
							<xsl:value-of
								select="concat($len, $stat, $type, $biblvl, '  22', $baod, $enclvl, $dcf, ' 45  ')"
							/>
						</leader>
						<xsl:for-each select="marc:controlfield[@tag = '001']">
							<controlfield tag="001">
								<xsl:value-of select="text()"/>
							</controlfield>
						</xsl:for-each>
						<xsl:for-each select="marc:controlfield[@tag = '005']">
							<controlfield tag="005">
								<xsl:value-of select="text()"/>
							</controlfield>
						</xsl:for-each>
						<xsl:for-each select="marc:controlfield[@tag = '008']">
							<!-- FIXME: Dummy indicators -->
							<datafield tag="100">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<subfield code="a">
									<xsl:variable name="deof">
										<xsl:choose>
											<xsl:when test="substring(text(), 1, 2) &lt; 70">
												<xsl:value-of
												select="concat('20', substring(text(), 1, 6))"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of
												select="concat('19', substring(text(), 1, 6))"/>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="topd" select="substring(text(), 7, 1)"/>
									<xsl:variable name="d1" select="substring(text(), 8, 4)"/>
									<xsl:variable name="d2" select="substring(text(), 12, 4)"/>
									<xsl:variable name="il">
										<xsl:choose>
											<xsl:when test="substring(text(), 23, 1) = 'a'"
												>b||</xsl:when>
											<xsl:when test="substring(text(), 23, 1) = 'b'"
												>c||</xsl:when>
											<xsl:when test="substring(text(), 23, 1) = 'j'"
												>a||</xsl:when>
											<xsl:when test="substring(text(), 23, 1) = 'c'"
												>d||</xsl:when>
											<xsl:when test="substring(text(), 23, 1) = 'd'"
												>e||</xsl:when>
											<xsl:when test="substring(text(), 23, 1) = 'e'"
												>k||</xsl:when>
											<xsl:when test="substring(text(), 23, 1) = 'g'"
												>m||</xsl:when>
											<xsl:when test="substring(text(), 23, 1) = '|'"
												>|||</xsl:when>
											<xsl:when test="substring(text(), 23, 1) = ' '"
												>u||</xsl:when>
											<xsl:otherwise>u||</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="gpc">
										<xsl:choose>
											<xsl:when test="substring(text(), 29, 1) = 'f'"
												>a</xsl:when>
											<xsl:when test="substring(text(), 29, 1) = 's'"
												>b</xsl:when>
											<xsl:when test="substring(text(), 29, 1) = 'l'"
												>d</xsl:when>
											<xsl:when test="substring(text(), 29, 1) = 'c'"
												>e</xsl:when>
											<xsl:when test="substring(text(), 29, 1) = 'i'"
												>f</xsl:when>
											<xsl:when test="substring(text(), 29, 1) = 'z'"
												>g</xsl:when>
											<xsl:when test="substring(text(), 29, 1) = 'o'"
												>h</xsl:when>
											<xsl:when test="substring(text(), 29, 1) = 'u'"
												>u</xsl:when>
											<xsl:when test="substring(text(), 29, 1) = ' '"
												>y</xsl:when>
											<xsl:when test="substring(text(), 29, 1) = 'z'"
												>z</xsl:when>
											<xsl:when test="substring(text(), 29, 1) = '|'"
												>|</xsl:when>
											<xsl:otherwise>y</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="mrc">
										<xsl:choose>
											<xsl:when test="substring(text(), 39, 1) = ' '"
												>0</xsl:when>
											<xsl:otherwise>1</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="loc">
										<xsl:choose>
											<xsl:when
												test="datafield[@tag = '040']/subfield[@code = 'b']">
												<xsl:value-of
												select="marc:datafield[@tag = '040']/subfield[@code = 'b']"
												/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="'   '"/>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="tc">
										<xsl:choose>
											<xsl:when test="substring(text(), 39, 1) = 'o'"
												>b</xsl:when>
											<xsl:otherwise>y</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<!-- Demander à nicomo pour les 2 variables suivantes -->
									<xsl:variable name="cs">
										<xsl:value-of select="'    '"/>
									</xsl:variable>
									<xsl:variable name="acs">
										<xsl:value-of select="'    '"/>
									</xsl:variable>
									<xsl:variable name="aot" select="substring(text(), 34, 1)"/>
									<xsl:value-of
										select="concat($deof, $topd, $d1, $d2, $il, $gpc, $mrc, $loc, $tc, $cs, $acs, $aot)"
									/>
								</subfield>
							</datafield>
							<datafield tag="105">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<!-- Difficile de faire un bel algo pour les deux variables suivantes -->
								<subfield code="a">
									<xsl:variable name="ic">
										<xsl:value-of select="'    '"/>
									</xsl:variable>
									<xsl:variable name="focc">
										<xsl:value-of select="'    '"/>
									</xsl:variable>
									<xsl:variable name="cc">
										<xsl:value-of select="substring(text(), 30, 1)"/>
									</xsl:variable>
									<xsl:variable name="fi">
										<xsl:value-of select="substring(text(), 31, 1)"/>
									</xsl:variable>
									<xsl:variable name="ii">
										<xsl:value-of select="substring(text(), 32, 1)"/>
									</xsl:variable>
									<xsl:variable name="lc">
										<xsl:choose>
											<xsl:when test="substring(text(), 34, 1) = '1'"
												>a</xsl:when>
											<xsl:otherwise>|</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="bc">
										<xsl:choose>
											<xsl:when test="substring(text(), 35, 1) = ' '"
												>y</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="substring(text(), 35, 1)"/>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:value-of
										select="concat($ic, $focc, $cc, $fi, $ii, $lc, $bc)"/>
								</subfield>
							</datafield>
							<datafield tag="106">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<subfield code="a">
									<xsl:choose>
										<xsl:when test="substring(text(), 24, 1) = ' '">y</xsl:when>
										<xsl:otherwise>
											<xsl:value-of select="substring(text(), 24, 1)"/>
										</xsl:otherwise>
									</xsl:choose>
								</subfield>
							</datafield>
							<datafield tag="110">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<subfield code="a">
									<xsl:variable name="tos">
										<xsl:choose>
											<xsl:when test="substring(text(), 22, 1) = 'p'"
												>a</xsl:when>
											<xsl:when test="substring(text(), 22, 1) = 'm'"
												>b</xsl:when>
											<xsl:when test="substring(text(), 22, 1) = 'n'"
												>c</xsl:when>
											<xsl:when test="substring(text(), 22, 1) = ' '"
												>z</xsl:when>
											<xsl:when test="substring(text(), 22, 1) = '|'"
												>|</xsl:when>
											<xsl:otherwise>z</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="foi">
										<xsl:choose>
											<xsl:when test="substring(text(), 19, 1) = 'd'"
												>a</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'c'"
												>b</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'w'"
												>c</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'e'"
												>d</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 's'"
												>e</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'm'"
												>f</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'b'"
												>g</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'q'"
												>h</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 't'"
												>i</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'f'"
												>j</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'a'"
												>k</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'g'"
												>l</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'h'"
												>m</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'i'"
												>n</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'j'"
												>o</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'u'"
												>u</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = ' '"
												>y</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'z'"
												>z</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = '|'"
												>|</xsl:when>
											<xsl:when test="substring(text(), 19, 1) = 'n'"
												>|</xsl:when>
											<xsl:otherwise>y</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="r">
										<xsl:choose>
											<xsl:when test="substring(text(), 20, 1) = 'r'"
												>a</xsl:when>
											<xsl:when test="substring(text(), 20, 1) = 'n'"
												>b</xsl:when>
											<xsl:when test="substring(text(), 20, 1) = 'u'"
												>u</xsl:when>
											<xsl:when test="substring(text(), 20, 1) = 'x'"
												>y</xsl:when>
											<xsl:when test="substring(text(), 20, 1) = '|'"
												>|</xsl:when>
											<xsl:when test="substring(text(), 20, 1) = ' '"
												>|</xsl:when>
											<xsl:otherwise>u</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="tomc">
										<xsl:choose>
											<xsl:when test="substring(text(), 25, 1) = 'b'"
												>a</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'c'"
												>b</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'i'"
												>c</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'a'"
												>d</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'd'"
												>e</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'e'"
												>f</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'r'"
												>g</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'y'"
												>h</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 's'"
												>i</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'p'"
												>j</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'o'"
												>k</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'l'"
												>l</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'w'"
												>m</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'g'"
												>n</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'v'"
												>o</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'h'"
												>p</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = 'n'"
												>r</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = ' '"
												>z</xsl:when>
											<xsl:when test="substring(text(), 25, 1) = '|'"
												>|</xsl:when>
											<xsl:otherwise>z</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="nocc">
										<xsl:value-of select="substring(text(), 26, 3)"/>
									</xsl:variable>
									<xsl:variable name="ci">
										<xsl:value-of select="substring(text(), 30, 1)"/>
									</xsl:variable>
									<xsl:variable name="tpa">|</xsl:variable>
									<xsl:variable name="iac">|</xsl:variable>
									<xsl:variable name="cia">|</xsl:variable>
									<xsl:value-of
										select="concat($tos, $foi, $r, $tomc, $nocc, $ci, $tpa, $iac, $cia)"
									/>
								</subfield>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '020']">
							<datafield tag="010">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '022']">
							<datafield tag="011">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='?']"><subfield code="b"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<!--<xsl:for-each select="marc:subfield[@code='?']"><subfield code="d"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = 'y']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='z']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
							</datafield>
						</xsl:for-each>
						<!--<xsl:for-each select="marc:datafield[@tag='024']">
					<datafield tag="012">
						<xsl:attribute name="ind1"><xsl:value-of select="@ind1" /></xsl:attribute>
						<xsl:attribute name="ind2"><xsl:value-of select="@ind2" /></xsl:attribute>
						<xsl:for-each select="marc:subfield[@code='a']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>
						<xsl:for-each select="marc:subfield[@code='b']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>
						<xsl:for-each select="marc:subfield[@code='z']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>
					</datafield>
				</xsl:for-each>-->
						<xsl:for-each select="marc:datafield[@tag = '015']">
							<datafield tag="020">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = '2']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '017']">
							<datafield tag="021">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '086']">
							<datafield tag="22">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = '2']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '030']">
							<datafield tag="040">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '028']">
							<datafield tag="071">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:choose>
										<xsl:when test="@ind2 = 0">0</xsl:when>
										<xsl:otherwise>1</xsl:otherwise>
									</xsl:choose>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '041']">
							<datafield tag="101">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'e']">
									<subfield code="h">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'f']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="i">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'h']">
									<subfield code="c">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '044']">
							<datafield tag="102">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='b']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '245']">
							<datafield tag="200">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
									<xsl:if test="contains(text(), ' = ')">
										<subfield code="d">
											<xsl:value-of
												select="concat('=', substring-after(text(), ' ='))"
											/>
										</subfield>
									</xsl:if>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<xsl:choose>
										<xsl:when test="contains(text(), ' / ')">
											<subfield code="f">
												<xsl:value-of
												select="substring-before(text(), ' / ')"/>
											</subfield>
											<subfield code="g">
												<xsl:value-of
												select="substring-after(text(), ' / ')"/>
											</subfield>
										</xsl:when>
										<xsl:otherwise>
											<subfield code="f">
												<xsl:value-of select="text()"/>
											</subfield>
										</xsl:otherwise>
									</xsl:choose>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="h">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'p']">
									<subfield code="i">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
							<!-- FIXME -->
							<!--
					<datafield tag="204">
						<xsl:attribute name="ind1"><xsl:value-of select="' '" /></xsl:attribute>
						<xsl:attribute name="ind2"><xsl:value-of select="' '" /></xsl:attribute>
						<xsl:for-each select="marc:subfield[@code='h']"><subfield code="a"><xsl:value-of select="text()" /></subfield></xsl:for-each>
					</datafield>
					-->
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '250']">
							<datafield tag="205">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '254']">
							<datafield tag="208">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '260']">
							<datafield tag="210">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="c">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'e']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'f']">
									<subfield code="g">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="h">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '263']">
							<datafield tag="211">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '300']">
							<datafield tag="215">
								<xsl:choose>
									<xsl:when test="@ind = 1">
										<xsl:attribute name="ind1">0</xsl:attribute>
									</xsl:when>
									<xsl:otherwise>
										<xsl:attribute name="ind1">1</xsl:attribute>
									</xsl:otherwise>
								</xsl:choose>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="c">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'e']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '490']">
							<datafield tag="225">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'v']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '256']">
							<datafield tag="230">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '500']">
							<datafield tag="300">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '525']">
							<datafield tag="300">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '555']">
							<datafield tag="300">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '504']">
							<datafield tag="320">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '505']">
							<datafield tag="327">
								<!-- FIXME: Dummy indicators -->
								<!--<xsl:attribute name="ind1"><xsl:value-of select="@ind1" /></xsl:attribute>-->
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<!--<xsl:attribute name="ind2"><xsl:value-of select="@ind2" /></xsl:attribute>-->
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<subfield code="a">bla</subfield>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '502']">
							<datafield tag="328">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '520']">
							<datafield tag="330">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '524']">
							<datafield tag="332">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '521']">
							<datafield tag="333">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '500']">
							<datafield tag="336">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '538']">
							<datafield tag="337">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '037']">
							<datafield tag="345">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'f']">
									<subfield code="c">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '760']">
							<datafield tag="410">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '762']">
							<datafield tag="411">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '770']">
							<datafield tag="421">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '772']">
							<datafield tag="422">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '777']">
							<datafield tag="423">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '780']">
							<datafield tag="430">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '785']">
							<datafield tag="440">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '775']">
							<datafield tag="451">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '776']">
							<datafield tag="452">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '767']">
							<datafield tag="453">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '765']">
							<datafield tag="454">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '787']">
							<datafield>
								<xsl:choose>
									<xsl:when
										test="contains(subfield[@code = 'i'], 'Reproduction of:')">
										<xsl:attribute name="tag">
											<xsl:value-of select="455" />
										</xsl:attribute>
									</xsl:when>
									<xsl:when
										test="contains(subfield[@code = 'i'], 'Reproduced as:')">
										<xsl:attribute name="tag">
											<xsl:value-of select="456" />
										</xsl:attribute>
									</xsl:when>
									<xsl:when
										test="contains(subfield[@code = 'i'], 'Item reviewed:')">
										<xsl:attribute name="tag">
											<xsl:value-of select="470" />
										</xsl:attribute>
									</xsl:when>
									<xsl:otherwise>
										<xsl:attribute name="tag">
											<xsl:value-of select="488" />
										</xsl:attribute>
									</xsl:otherwise>
								</xsl:choose>
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '774']">
							<datafield>
								<xsl:choose>
									<xsl:when test="subfield[@code = 'i']">
										<xsl:attribute name="tag">
											<xsl:value-of select="462" />
										</xsl:attribute>
									</xsl:when>
									<xsl:otherwise>
										<xsl:attribute name="tag">
											<xsl:value-of select="461" />
										</xsl:attribute> 
									</xsl:otherwise>
								</xsl:choose>
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '773']">
							<datafield tag="463">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '774']">
							<datafield tag="464">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'w']">
									<subfield code="3">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '730']">
							<datafield tag="500">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="n">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'f']">
									<subfield code="k">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="n">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'k']">
									<subfield code="j">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'l']">
									<subfield code="m">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'm']">
									<subfield code="r">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="h">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'o']">
									<subfield code="w">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'p']">
									<subfield code="i">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'r']">
									<subfield code="u">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 's']">
									<subfield code="q">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '243']">
							<datafield tag="501">
								<xsl:attribute name="ind1">1</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'k']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'f']">
									<subfield code="k">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'l']">
									<subfield code="m">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '247']">
							<datafield tag="520">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="h">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'p']">
									<subfield code="i">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="n">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'f']">
									<subfield code="j">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '222']">
							<datafield tag="530">
								<xsl:attribute name="ind1">0</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '210']">
							<datafield tag="531">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '246']">
							<datafield tag="532">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">0</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '242']">
							<datafield tag="541">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="h">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'p']">
									<subfield code="i">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'y']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '773']">
							<datafield tag="545">
								<xsl:attribute name="ind1">
									<xsl:choose>
										<xsl:when test="@ind1 = 0">1</xsl:when>
										<xsl:otherwise>0</xsl:otherwise>
									</xsl:choose>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '610']">
							<datafield tag="601">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
									<subfield code="c">
										<xsl:value-of
											select="substring-before(substring-after(text(), '('), ')')"
										/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'e']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='f']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<!--<xsl:for-each select="marc:subfield[@code='g']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = 'k']">
									<subfield code="j">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='l']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<!--<xsl:for-each select="marc:subfield[@code='m']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='o']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<!--<xsl:for-each select="marc:subfield[@code='p']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<!--<xsl:for-each select="marc:subfield[@code='r']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<!--<xsl:for-each select="marc:subfield[@code='s']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<!--<xsl:for-each select="marc:subfield[@code='t']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<!--<xsl:for-each select="marc:subfield[@code='u']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'y']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='?']"><subfield code="3"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '611']">
							<datafield tag="601">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
									<subfield code="c">
										<xsl:value-of
											select="substring-before(substring-after(text(), '('), ')')"
										/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'e']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='f']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<!--<xsl:for-each select="marc:subfield[@code='g']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = 'k']">
									<subfield code="j">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='l']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='p']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<!--<xsl:for-each select="marc:subfield[@code='s']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='u']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'y']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='?']"><subfield code="3"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '630']">
							<datafield tag="605">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='d']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = 'f']">
									<subfield code="k">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="n">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'k']">
									<subfield code="j">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'l']">
									<subfield code="m">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'm']">
									<subfield code="r">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="h">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'o']">
									<subfield code="w">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'p']">
									<subfield code="i">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'r']">
									<subfield code="u">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 's']">
									<subfield code="q">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='t']"><subfield code="?"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'y']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='?']"><subfield code="3"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '600']">
							<datafield tag="600">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:choose>
										<xsl:when test="@ind1 = 0">0</xsl:when>
										<xsl:otherwise>1</xsl:otherwise>
									</xsl:choose>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="substring-before(text(), ', ')"/>
									</subfield>
									<subfield code="b">
										<xsl:value-of select="substring-after(text(), ', ')"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="c">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'y']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '2']">
									<subfield code="2">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
							<datafield tag="602">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 't']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'y']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '2']">
									<subfield code="2">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '630']">
							<datafield tag="605">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="h">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'p']">
									<subfield code="i">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'f']">
									<subfield code="k">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'k']">
									<subfield code="l">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'l']">
									<subfield code="m">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'g']">
									<subfield code="n">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 's']">
									<subfield code="q">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'r']">
									<subfield code="r">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="s">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'o']">
									<subfield code="t">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'r']">
									<subfield code="u">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'y']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '2']">
									<subfield code="2">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '650']">
							<datafield tag="606">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'y']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '2']">
									<subfield code="2">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '651']">
							<datafield tag="607">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="substring-before(text(), ', ')"/>
									</subfield>
									<subfield code="b">
										<xsl:value-of select="substring-after(text(), ', ')"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'x']">
									<subfield code="x">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'z']">
									<subfield code="y">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'y']">
									<subfield code="z">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '2']">
									<subfield code="2">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '653']">
							<datafield tag="610">
								<xsl:attribute name="ind1">
									<xsl:choose>
										<xsl:when test="@ind1 = ' '">0</xsl:when>
										<xsl:otherwise>
											<xsl:value-of select="@ind1"/>
										</xsl:otherwise>
									</xsl:choose>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '752']">
							<datafield tag="620">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield">
									<subfield code="@code">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '753']">
							<datafield tag="626">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield">
									<subfield code="@code">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '043']">
							<datafield tag="660">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield">
									<subfield code="@code">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '045']">
							<datafield tag="661">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '886']">
							<datafield tag="670">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="c">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '2']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '080']">
							<datafield tag="675">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '082']">
							<datafield tag="676">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '2']">
									<subfield code="v">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '050']">
							<datafield tag="680">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '084']">
							<datafield tag="686">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '2']">
									<subfield code="2">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '100']">
							<datafield tag="700">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="substring-before(text(), ', ')"/>
									</subfield>
									<subfield code="b">
										<xsl:value-of select="substring-after(text(), ', ')"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="c">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'e']">
									<subfield code="4">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'q']">
									<subfield code="g">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'u']">
									<subfield code="p">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='?']"><subfield code="3"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = '4']">
									<subfield code="4">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '700']">
							<datafield tag="701">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="substring-before(text(), ', ')"/>
									</subfield>
									<subfield code="b">
										<xsl:value-of select="substring-after(text(), ', ')"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="c">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'e']">
									<subfield code="4">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'q']">
									<subfield code="g">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'u']">
									<subfield code="p">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<!--<xsl:for-each select="marc:subfield[@code='?']"><subfield code="3"><xsl:value-of select="text()" /></subfield></xsl:for-each>-->
								<xsl:for-each select="marc:subfield[@code = '4']">
									<subfield code="4">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '110']">
							<datafield tag="710">
								<xsl:attribute name="ind1">0</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'u']">
									<subfield code="p">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '4']">
									<subfield code="4">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '111']">
							<datafield tag="710">
								<xsl:attribute name="ind1">1</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'e']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'u']">
									<subfield code="p">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '4']">
									<subfield code="4">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '710']">
							<datafield tag="711">
								<xsl:attribute name="ind1">0</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'b']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'u']">
									<subfield code="p">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '4']">
									<subfield code="4">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '711']">
							<datafield tag="711">
								<xsl:attribute name="ind1">1</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'e']">
									<subfield code="b">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'n']">
									<subfield code="d">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'c']">
									<subfield code="e">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'u']">
									<subfield code="p">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '4']">
									<subfield code="4">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '100']">
							<datafield tag="720">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '4']">
									<subfield code="4">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '700']">
							<datafield tag="721">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = 'd']">
									<subfield code="f">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
								<xsl:for-each select="marc:subfield[@code = '4']">
									<subfield code="4">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:controlfield[@tag = '008']">
							<datafield tag="802">
								<xsl:attribute name="ind1">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="' '"/>
								</xsl:attribute>
								<subfield code="a">
									<xsl:choose>
										<xsl:when test="substring(text(), 21, 1) = '0'"
											>00</xsl:when>
										<xsl:when test="substring(text(), 21, 1) = '1'"
											>01</xsl:when>
										<xsl:when test="substring(text(), 21, 1) = '4'"
											>04</xsl:when>
										<xsl:when test="substring(text(), 21, 1) = '#'"
											>uu</xsl:when>
										<xsl:when test="substring(text(), 21, 1) = 'z'"
											>zz</xsl:when>
										<xsl:otherwise>zz</xsl:otherwise>
									</xsl:choose>
								</subfield>
							</datafield>
						</xsl:for-each>
						<xsl:for-each select="marc:datafield[@tag = '590']">
							<datafield tag="900">
								<xsl:attribute name="ind1">
									<xsl:value-of select="@ind1"/>
								</xsl:attribute>
								<xsl:attribute name="ind2">
									<xsl:value-of select="@ind2"/>
								</xsl:attribute>
								<xsl:for-each select="marc:subfield[@code = 'a']">
									<subfield code="a">
										<xsl:value-of select="text()"/>
									</subfield>
								</xsl:for-each>
							</datafield>
						</xsl:for-each>
						
						
						<xsl:call-template name="selects">
							<xsl:with-param name="i">900</xsl:with-param>
							<xsl:with-param name="count">1000</xsl:with-param>
						</xsl:call-template>
						
					</record>
				</xsl:for-each>
			</xsl:for-each>
		</collection>
	</xsl:template>
	
	<xsl:template name="selects">
		<xsl:param name="i" />
		<xsl:param name="count" />
		
		<xsl:if test="$i &lt;= $count">
			<xsl:for-each select="marc:datafield[@tag=$i]">
			<datafield>
				<xsl:attribute name="tag"><xsl:value-of select="@tag" /></xsl:attribute>
				<xsl:attribute name="ind1">
					<xsl:value-of select="@ind1"/>
				</xsl:attribute>
				<xsl:attribute name="ind2">
					<xsl:value-of select="@ind2"/>
				</xsl:attribute>
				<xsl:for-each select="marc:subfield[@code]">
					<subfield>
						<xsl:attribute name="code">
							<xsl:value-of select="@code" />
						</xsl:attribute>
						<xsl:value-of select="text()"/>
					</subfield>
				</xsl:for-each>
			</datafield>
			</xsl:for-each>
		</xsl:if>
		
		<!--begin_: RepeatTheLoopUntilFinished-->
		<xsl:if test="$i &lt; $count">
			<xsl:call-template name="selects">
				<xsl:with-param name="i">
					<xsl:value-of select="$i + 1"/>
				</xsl:with-param>
				<xsl:with-param name="count">
					<xsl:value-of select="$count"/>
				</xsl:with-param>
			</xsl:call-template>
		</xsl:if>
	</xsl:template>
</xsl:stylesheet>
