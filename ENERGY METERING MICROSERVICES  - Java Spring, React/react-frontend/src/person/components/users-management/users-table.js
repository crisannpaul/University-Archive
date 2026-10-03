import React from "react";
import Table from "../../../commons/tables/table";


const columns = [
    {
        Header: 'ID',
        accessor: 'userId',
    },
    {
        Header: 'Username',
        accessor: 'username',
    },
    {
        Header: 'Email',
        accessor: 'email',
    },
    {
        Header: 'Role',
        accessor: 'role',
    }
];

const filters = [
];

class PersonTable extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            tableData: this.props.tableData
        };
    }

    render() {
        return (
            <Table
                data={this.state.tableData}
                columns={columns}
                search={filters}
                pageSize={5}
            />
        )
    }
}

export default PersonTable;