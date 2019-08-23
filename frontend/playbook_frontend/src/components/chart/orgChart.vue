<template>
  <div>
    <Container :datasource="chartData" @node-click="test_user($event)" :pan="pan" :zoom="zoom"></Container>

    <el-drawer
      :title="dialogData.type"
      :visible.sync="dialog"
      direction="rtl"
      size="50%">
      <br>
      <br>
      <br>
      <span style="margin-left: 3%;">{{ dialogData.type }}  Name : </span>
      <p style="margin-left: 5%;"> {{ dialogData.name }} </p>
      <el-divider></el-divider>
      <span style="margin-left: 3%;">Description:</span>
      <p style="margin-left: 5%;">{{ dialogData.title }}</p>
    </el-drawer>
  </div>
</template>

<script>
import Container from '@/components/chart/OrganizationChartContainer'

export default {
  name: 'orgChart',
  components: {
    // OrganizationChart,
    Container
  },
  props: {
    chartData: {
      required: false,
      default: {}
    }
  },
  data () {
    return {
      pan: true,
      zoom: false,
      dialog: false,
      dialogData: '',
      ds: {
        'id': '1',
        'name': 'Lao Lao',
        'title': 'general manager',
        'children': [
          {'id': '2', 'name': 'Bo Miao', 'title': 'department manager'},
          {
            'id': '3',
            'name': 'Su Miao',
            'title': 'department manager',
            'children': [
              {'id': '4', 'name': 'Tie Hua', 'title': 'senior engineer'},
              {
                'id': '5',
                'name': 'Hei Hei',
                'title': 'senior engineer',
                'children': [
                  {'id': '6', 'name': 'Pang Pang', 'title': 'engineer'},
                  {'id': '7', 'name': 'Xiang Xiang', 'title': 'UE engineer'}
                ]
              }
            ]
          },
          {'id': '8', 'name': 'Hong Miao', 'title': 'department manager'},
          {'id': '9', 'name': 'Chun Miao', 'title': 'department manager'}
        ]
      }
    }
  },
  methods: {
    test_user (data) {
      this.dialog = true
      this.dialogData = ''
      this.dialogData = data
    }
  }
}
</script>

<style scoped>

</style>
