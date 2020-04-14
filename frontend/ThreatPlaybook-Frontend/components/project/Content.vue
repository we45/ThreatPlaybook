<template>
  <div>
    <v-row>
      <v-col cols="6">
        <v-card>
          <v-card-title class="subtitle-1"
            >Vulnerabilities by Severity</v-card-title
          >
          <v-card-text>
            <apexchart
              type="pie"
              :options="pieOptions"
              :series="pieSeries"
              height="300"
            ></apexchart>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card>
          <v-card-title class="subtitle-1">List of Scans</v-card-title>
          <v-card-text>
            <v-simple-table height="300px">
              <template v-slot:default>
                <thead>
                  <tr>
                    <th class="text-left">Name</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in scanData" :key="item.name">
                    <td>{{ item.name }}</td>
                    <td>
                      <v-btn
                        color="primary"
                        small
                        @click="viewScanPage(item.name)"
                        >View</v-btn
                      >
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>
<script>
export default {
  name: 'Content',
  props: {
    pieSeries: {
      required: false,
      type: Array
    },
    scanData: {
      required: false,
      type: Array
    }
  },
  data() {
    return {
      pieOptions: {
        labels: ['High', 'Medium', 'Low'],
        colors: ['#d11d55', '#ff9c2c', '#008b8f']
      }
    }
  },
  methods: {
    viewScanPage(data) {
      this.$router.push('/scan/' + data)
    }
  }
}
</script>
