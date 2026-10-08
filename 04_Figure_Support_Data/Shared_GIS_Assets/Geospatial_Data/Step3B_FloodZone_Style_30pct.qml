<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34" styleCategories="Symbology">
  <renderer-v2 attr="final_class" type="categorizedSymbol">
    <categories>
      <category value="SEVERE" label="Severe flood zone / 严重洪涝区域" symbol="0"/>
      <category value="RECURRENT" label="Recurrent flood zone / 经常内涝区域" symbol="1"/>
      <category value="MILD" label="Mild flood zone / 轻度内涝区域" symbol="2"/>
    </categories>
    <symbols>
      <symbol name="0" type="fill">
        <layer class="SimpleFill">
          <Option name="color" value="255,0,0,77"/>
          <Option name="outline_color" value="179,0,0,255"/>
          <Option name="outline_width" value="0.45"/>
        </layer>
      </symbol>
      <symbol name="1" type="fill">
        <layer class="SimpleFill">
          <Option name="color" value="255,215,0,77"/>
          <Option name="outline_color" value="179,143,0,255"/>
          <Option name="outline_width" value="0.45"/>
        </layer>
      </symbol>
      <symbol name="2" type="fill">
        <layer class="SimpleFill">
          <Option name="color" value="0,102,255,77"/>
          <Option name="outline_color" value="0,61,153,255"/>
          <Option name="outline_width" value="0.45"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>
