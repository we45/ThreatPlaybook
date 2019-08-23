<template>
  <div>
    <el-table
      :data="tableData"
      height="300"
      border
      style="width: 100%">
      <el-table-column
        prop="name"
        label="Name">
      </el-table-column>
      <!--    </el-table-column>-->
      <el-table-column
        fixed="right"
        label="Operations"
        width="120">
        <template slot-scope="scope">
          <el-tooltip class="item" effect="dark" content="View" placement="top">
          <el-button type="text" size="small" @click="viewClick(scope.row.name)">
            <i class="el-icon-position" style="font-size: 16px;"></i></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'scanTable',
  props: {
    tableData: {
      type: Array
    }
  },
  methods: {
    viewClick (name) {
      this.$emit('viewScan', {name: name})
    }
  }
}
</script>

<style scoped>

</style>
