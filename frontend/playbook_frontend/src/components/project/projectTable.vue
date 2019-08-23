<template>
  <div>
    <br>
    <el-table
      :data="tableData"
      height="250"
      style="width: 100%">
      <el-table-column
        prop="name"
        label="Name">
      </el-table-column>
      <!--    <el-table-column-->
      <!--      prop="name"-->
      <!--      label="Name"-->
      <!--      width="180">-->
      <!--    </el-table-column>-->
      <!--    <el-table-column-->
      <!--      prop="address"-->
      <!--      label="Address">-->
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
<!--          <el-tooltip class="item" effect="dark" content="Edit" placement="top">-->
<!--          <el-button type="text" size="small">-->
<!--            <i class="el-icon-edit" style="font-size: 16px;"></i></el-button>-->
<!--          </el-tooltip>-->
<!--          <el-tooltip class="item" effect="dark" content="Delete" placement="top">-->
<!--          <el-button @click="deleteClick(scope.$index, scope.row.id)" type="text" size="small">-->
<!--            <i class="el-icon-delete" style="font-size: 16px;"></i>-->
<!--          </el-button>-->
<!--          </el-tooltip>-->
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'projectTable',
  props: {
    tableData: {
      type: Array
    }
  },
  methods: {
    deleteClick (scope, name) {
      console.log('scope', scope)
      console.log('click', name)
    },
    viewClick (name) {
      this.$emit('viewproject', {name: name})
    }
  }
}
</script>

<style scoped>

</style>
