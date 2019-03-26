<template>
    <div>
        <loading :active.sync="isLoading" :can-cancel="true" :is-full-page="isLoading"></loading>
        <nav-bar></nav-bar>
        <!--<b-container fluid>-->
            <!--<br>-->
            <!--<h4> Scan Name : {{ actual_scan_name }}</h4>-->
            <!--<hr>-->
            <!--<template v-for="(vul, index) in scanVuls.vulnerabilities">-->
                <!--<b-card no-body class="mb-1">-->
                    <!--<b-card-header header-tag="header" class="p-1" role="tab">-->
                        <!--<b-button block href="#" v-b-toggle="'scan_vul-'+index"-->
                                  <!--style="text-align: left;background-color: #CCCCCC;color: #7957d5">{{ vul.name }}-->
                            <!--<span class="label-high" v-if="vul.severity === 3" style="float: right;">High</span>-->
                            <!--<span class="label-medium" v-if="vul.severity === 2" style="float: right;">Medium</span>-->
                            <!--<span class="label-low" v-if="vul.severity === 1" style="float: right;">Low</span>-->
                        <!--</b-button>-->
                    <!--</b-card-header>-->
                    <!--<b-collapse :id="'scan_vul-'+index" visible accordion="my-accordion" role="tabpanel">-->
                        <!--<br>-->
                        <!--<br>-->
                        <!--<b-container fluid>-->
                            <!--<b-row>-->
                                <!--<b-col cols="6">-->
                                    <!--<p class="text-left">-->
                                        <!--<span>CWE</span>-->
                                        <!--<span>:</span>-->
                                        <!--<span>{{ vul.cwe }}</span>-->
                                    <!--</p>-->
                                <!--</b-col>-->
                                <!--<b-col cols="6">-->
                                        <!--<p class="text-left">-->
                                        <!--<span>Tool</span>-->
                                        <!--<span>:</span>-->
                                        <!--<span>{{ vul.tool }}</span>-->
                                    <!--</p>-->
                                <!--</b-col>-->
                            <!--</b-row>-->
                            <!--<b-row v-if="vul.description">-->
                                <!--<b-col>-->
                                    <!--<h6>Description</h6>-->
                                    <!--<p class="text-justify">-->
                                        <!--{{ vul.description }}-->
                                    <!--</p>-->
                                <!--</b-col>-->
                                <!--<br>-->
                            <!--</b-row>-->
                            <!--<b-row v-if="vul.remediation">-->
                                <!--<b-col>-->
                                    <!--<h6>Remediation</h6>-->
                                    <!--<p class="text-justify">-->
                                        <!--{{ vul.remediation }}-->
                                    <!--</p>-->
                                <!--</b-col>-->
                            <!--</b-row>-->
                            <!--<br>-->
                            <!--<b-row v-if="vul.observation">-->
                                <!--<b-col>-->
                                    <!--<h6>Observation</h6>-->
                                    <!--<p class="text-justify">-->
                                        <!--{{ vul.observation }}-->
                                    <!--</p>-->
                                <!--</b-col>-->
                            <!--</b-row>-->
                        <!--</b-container>-->
                    <!--</b-collapse>-->
                <!--</b-card>-->
            <!--</template>-->
        <!--</b-container>-->

        <b-container fluid>
    <!-- User Interface controls -->
            <br>
            <h4> Scan Name : {{ actual_scan_name }}</h4>
            <hr>
    <b-row>
      <b-col md="6" class="my-1">

      </b-col>

      <b-col md="6" class="my-1">
      </b-col>

      <b-col md="6" class="my-1">
          <b-form-group label-cols-sm="3" label="Per page" class="mb-0">
          <b-form-select :options="pageOptions" v-model="perPage" />
        </b-form-group>
      </b-col>

      <b-col md="6" class="my-1">
       <b-pagination
          :total-rows="totalRows"
          :per-page="perPage"
          v-model="currentPage"
          class="my-0"
        />
      </b-col>
    </b-row>

    <!-- Main table element -->
    <b-table
      show-empty
      stacked="md"
      :items="items"
      :fields="fields"
      :current-page="currentPage"
      :per-page="perPage"
    >
      <template slot="name" slot-scope="row">
        {{ row.value }}
      </template>

      <template slot="severity" slot-scope="row">
                <span class="label-high" v-if="row.value === 3" style="float: right;">High</span>
                <span class="label-medium" v-if="row.value === 2" style="float: right;">Medium</span>
                <span class="label-low" v-if="row.value === 1" style="float: right;">Low</span>
      </template>
        <template slot="remediation" slot-scope="row">

      </template>
        <template slot="observation" slot-scope="row">

      </template>

      <template slot="description" slot-scope="row">
        <b-button size="sm" @click="row.toggleDetails">
          {{ row.detailsShowing ? 'Hide' : 'Show' }} Details
        </b-button>
      </template>

      <template slot="row-details" slot-scope="row">
        <b-card>
          <ul>
                <b-row>
                                <b-col cols="6" v-if="row.item.cwe">
                                    <p class="text-left">
                                        <span>CWE</span>
                                        <span>:</span>
                                        <span>{{ row.item.cwe }}</span>
                                    </p>
                                </b-col>
                                <b-col cols="6" v-if="row.item.tool">
                                        <p class="text-left">
                                        <span>Tool</span>
                                        <span>:</span>
                                        <span>{{ row.item.tool }}</span>
                                    </p>
                                </b-col>
                            </b-row>
                            <b-row v-if="row.item.description">
                                <b-col>
                                    <h6>Description</h6>
                                    <p class="text-justify">
                                        {{ row.item.description }}
                                    </p>
                                </b-col>
                                <br>
                            </b-row>
                            <b-row v-if="row.item.remediation">
                                <b-col>
                                    <h6>Remediation</h6>
                                    <p class="text-justify">
                                        {{ row.item.remediation }}
                                    </p>
                                </b-col>
                            </b-row>
                            <br>
                            <b-row v-if="row.item.observation">
                                <b-col>
                                    <h6>Observation</h6>
                                    <p class="text-justify">
                                        {{ row.item.observation }}
                                    </p>
                                </b-col>
                            </b-row>
          </ul>
        </b-card>
      </template>
    </b-table>

    <b-row>
      <b-col md="6" class="my-1">

      </b-col>
    </b-row>

  </b-container>
    </div>
</template>

<script>
    import Navbar from "./Navbar.vue";
    import Loading from 'vue-loading-overlay'
    import 'vue-loading-overlay/dist/vue-loading.css';
    import axios from '../utils/auth'
    const items = ''
    export default {
        name: 'Scan',
        components: {
            "nav-bar": Navbar,
            Loading
        },
        created() {
            this.scan_name = this.$route.params.scanName
            this.actual_scan_name = atob(this.$route.params.scanName)
            this.fetchData()
        },
        data() {
            return {
                isLoading: false,
                scanVuls: '',
                items: '',
            fields: [
              { key: 'name', label: 'Vulnerability'},
              { key: 'severity', label: 'Severity'},
              { key: 'cwe', label: 'CWE'},
              { key: 'remediation', label: ''},
              { key: 'observation', label: ''},
              { key: 'description', label: 'Action'}
            ],
            currentPage: 1,
            perPage: 5,
            totalRows: 0,
            pageOptions: [5, 10, 15],
            modalInfo: { title: '', content: '' }}
        },
        methods: {
            fetchData() {
                this.isLoading = true
                const scanName = `"${this.actual_scan_name}"`
                axios.post('/graph', {
                    query: '{\n' +
                        'vulsByScan(scanName:' + scanName + '){\n' +
                        'vulnerabilities{ \n' +
                        'name\n' +
                        'severity\n' +
                        'cwe\n' +
                        'tool\n' +
                        'description\n' +
                        'remediation\n' +
                        'observation\n' +

                        '}\n' +
                        '}\n' +
                        '}'
                })
                    .then(res => {
                        this.isLoading = false
                        this.scanVuls = res.data.data.vulsByScan
                        this.items = res.data.data.vulsByScan.vulnerabilities
                        this.totalRows = this.items.length
                    })
                    .catch(error => {
                        this.isLoading = false
                    })
            },

      resetModal() {
        this.modalInfo.title = ''
        this.modalInfo.content = ''
      },
      onFiltered(filteredItems) {
        // Trigger pagination to update the number of buttons/pages due to filtering
        this.totalRows = filteredItems.length
        this.currentPage = 1
      }
        }

    }
</script>

<style scoped>
    .label-high {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #FFFFFF;
        background-color: #d11d55 !important
    }

    .label-medium {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #FFFFFF;
        background-color: #ff9c2c !important
    }

    .label-low {
        width: 60px;
        border-radius: 0;
        text-shadow: none;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 5px 3px;
        text-align: center;
        color: #FFFFFF;
        background-color: #008b8f !important
    }
</style>
