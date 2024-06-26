def get_all_posts(page, supabase):
    response = supabase.table('create-job-v1').select("*").execute()
    all_data = response.data
    sorted_data = sorted(all_data, key=lambda x: x['created_at'], reverse=True)
    latest_datetime = sorted_data[0]['created_at']
    page_size = 5
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    limited_data = sorted_data[start_index:end_index]

    total_pages = len(all_data) / page_size
    if total_pages % 1 != 0:
        total_pages = int(total_pages) + 1

    return {
        "data": limited_data,
        "latest_datetime": latest_datetime,
        "total_pages": total_pages
    }
